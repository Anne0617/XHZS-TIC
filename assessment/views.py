from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = "corporate/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["section"] = "home"
        return ctx
