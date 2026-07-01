from django.views.generic import TemplateView

class CorporateHomeView(TemplateView):
    template_name = "corporate/home.html"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["section"] = "home"
        return ctx

class ProductView(TemplateView):
    template_name = "corporate/product.html"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["section"] = "product"
        return ctx

class SolutionsView(TemplateView):
    template_name = "corporate/solutions.html"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["section"] = "solutions"
        return ctx

class AboutView(TemplateView):
    template_name = "corporate/about.html"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["section"] = "about"
        return ctx

class JoinView(TemplateView):
    template_name = "corporate/join.html"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["section"] = "join"
        return ctx
