from django.urls import path
from . import views_corporate as cv

urlpatterns = [
    path("product/", cv.ProductView.as_view(), name="corporate_product"),
    path("solutions/", cv.SolutionsView.as_view(), name="corporate_solutions"),
    path("about/", cv.AboutView.as_view(), name="corporate_about"),
    path("join/", cv.JoinView.as_view(), name="corporate_join"),
]
