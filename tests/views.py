from django.views.generic.base import TemplateView


class SignIn(TemplateView):
    template_name = "signin.html"


class About(TemplateView):
    template_name = "about.html"


class Welcome(TemplateView):
    template_name = "welcome.html"


class ChooseDeduct(TemplateView):
    template_name = "chooseDeductible.html"


class LetsStart(TemplateView):
    template_name = "letsStart.html"

