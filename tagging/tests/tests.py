import logging

import pytest

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.contrib.contenttypes.models import ContentType

from tagging.models import TagGFK, TagExplicit, ProfileA, ProfileB, ProfileC, ProfileD, ProfileBExtra
from tagging.serializers import serialize_tag_gfk, serialize_tag_explicit



class TestForeignKeyRelations:

    @pytest.fixture(autouse=True)
    def setup_method(self, db):
        self.profile_a = ProfileA.objects.bulk_create([ProfileA(name=f"A{i}", age=i) for i in range(100)])
        self.profile_b = ProfileB.objects.bulk_create([ProfileB(name=f"B{i}", email="fakemail@gmail.com") for i in range(100)])
        self.profile_b_extra = ProfileBExtra.objects.bulk_create(
            [ProfileBExtra(profile_b=b, info=f"Extra info for B{i}") for i, b in enumerate(self.profile_b)]
        )
        self.profile_c = ProfileC.objects.bulk_create([ProfileC(name=f"C{i}", address="123 Main St") for i in range(100)])
        self.profile_d = ProfileD.objects.bulk_create([ProfileD(name=f"D{i}", phone="123-456-7890") for i in range(100)])

        self.profile_a_ct = ContentType.objects.get_for_model(ProfileA)
        self.profile_b_ct = ContentType.objects.get_for_model(ProfileB)
        self.profile_c_ct = ContentType.objects.get_for_model(ProfileC)
        self.profile_d_ct = ContentType.objects.get_for_model(ProfileD)


    def insert_gfk(self):
        TagGFK.objects.bulk_create(
            [TagGFK(content_type=self.profile_a_ct, object_id=a.id) for a in self.profile_a]
            + [TagGFK(content_type=self.profile_b_ct, object_id=b.id) for b in self.profile_b]
            + [TagGFK(content_type=self.profile_c_ct, object_id=c.id) for c in self.profile_c]
            + [TagGFK(content_type=self.profile_d_ct, object_id=d.id) for d in self.profile_d]
        )

    def insert_explicit(self):
        TagExplicit.objects.bulk_create(
            [TagExplicit(profile_a=a) for i, a in enumerate(self.profile_a)] +
            [TagExplicit(profile_b=b) for i, b in enumerate(self.profile_b)] +
            [TagExplicit(profile_c=c) for i, c in enumerate(self.profile_c)] +
            [TagExplicit(profile_d=d) for i, d in enumerate(self.profile_d)]
        )

    @pytest.mark.benchmark(
        group="inserts",
    )
    def test_insert_gfk(self, benchmark):
        benchmark(self.insert_gfk)

    @pytest.mark.benchmark(
        group="inserts",
    )
    def test_insert_explicit(self, benchmark):
        benchmark(self.insert_explicit)

    @pytest.mark.benchmark(
        group="serialization",
    )
    def test_serialize_gfk(self, benchmark):
        self.insert_gfk()
        benchmark(lambda :[serialize_tag_gfk(tag) for tag in TagGFK.objects.all()])

    @pytest.mark.benchmark(
        group="serialization",
    )
    def test_serialize_gfk_with_select_related(self, benchmark):
        self.insert_gfk()
        benchmark(lambda :[serialize_tag_gfk(tag) for tag in TagGFK.objects.select_related("content_type").all()])

    @pytest.mark.benchmark(
        group="serialization",
    )
    def test_serialize_gfk_with_prefetch_related(self, benchmark):
        self.insert_gfk()
        benchmark(lambda :[serialize_tag_gfk(tag) for tag in TagGFK.objects.all().prefetch_related("content_object")])

    def test_serialize_gfk_prefetch_related_error(self):
        self.insert_gfk()
        with pytest.raises( AttributeError, match="Cannot find 'extra_data' on Profile"):
            [serialize_tag_gfk(tag) for tag in TagGFK.objects.all().prefetch_related("content_object", "content_object__extra_data")]

    @pytest.mark.benchmark(
        group="serialization",
    )
    def test_serialize_explicit(self, benchmark):
        self.insert_explicit()
        benchmark(lambda :[serialize_tag_explicit(tag) for tag in TagExplicit.objects.all()])

    @pytest.mark.benchmark(
        group="serialization",
    )
    def test_serialize_explicit_with_select_related(self, benchmark):
        self.insert_explicit()
        benchmark(lambda :[serialize_tag_explicit(tag) for tag in TagExplicit.objects.select_related("profile_a", "profile_b", "profile_b__extra_data", "profile_c", "profile_d").all()])

    @pytest.mark.benchmark(
        group="queries",
    )
    def test_query_gfk_queries_and_perf(self, benchmark):
        self.insert_gfk()
        def serialize_and_capture():
            with CaptureQueriesContext(connection) as context:
                [serialize_tag_gfk(tag) for tag in TagGFK.objects.all()]
            return len(context.captured_queries)
        queries = benchmark(serialize_and_capture)
        logging.info(f"Number of queries for GFK serialization: {queries}")

    @pytest.mark.benchmark(
        group="queries",
    )
    def test_query_explicit_queries_and_perf(self, benchmark):
        self.insert_explicit()
        def serialize_and_capture():
            with CaptureQueriesContext(connection) as context:
                data = [serialize_tag_explicit(tag) for tag in TagExplicit.objects.all()]
            return len(context.captured_queries)
        queries = benchmark(serialize_and_capture)
        logging.info(f"Number of queries for Explicit serialization: {queries}")

    @pytest.mark.benchmark(
        group="queries",
    )
    def test_query_gfk_with_select_related_queries_and_perf(self, benchmark):
        self.insert_gfk()
        def serialize_and_capture():
            with CaptureQueriesContext(connection) as context:
                [serialize_tag_gfk(tag) for tag in TagGFK.objects.select_related("content_type").all()]
            return len(context.captured_queries)
        queries = benchmark(serialize_and_capture)
        logging.info(f"Number of queries for GFK serialization with select_related: {queries}")

    @pytest.mark.benchmark(
        group="queries",
    )
    def test_query_explicit_with_select_related_queries_and_perf(self, benchmark):
        self.insert_explicit()
        def serialize_and_capture():
            with CaptureQueriesContext(connection) as context:
                [serialize_tag_explicit(tag) for tag in TagExplicit.objects.select_related("profile_a", "profile_b", "profile_b__extra_data", "profile_c", "profile_d").all()]
            return len(context.captured_queries)
        queries = benchmark(serialize_and_capture)
        logging.info(f"Number of queries for Explicit serialization with select_related: {queries}")

    @pytest.mark.benchmark(
        group="queries",
    )
    def test_query_gfk_with_prefetch_related_queries_and_perf(self, benchmark):
        self.insert_gfk()
        def serialize_and_capture():
            with CaptureQueriesContext(connection) as context:
                [serialize_tag_gfk(tag) for tag in TagGFK.objects.all().prefetch_related("content_object")]
            return len(context.captured_queries)
        queries = benchmark(serialize_and_capture)
        logging.info(f"Number of queries for GFK serialization with prefetch_related: {queries}")
