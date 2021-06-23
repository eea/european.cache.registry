from flask.views import MethodView


class CrashMe(MethodView):
    def get(self):
        raise RuntimeError("Crashing as requested by you")
