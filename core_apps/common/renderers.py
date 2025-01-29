import json
from typing import Any, Optional, Union

from django.utils.translation import gettext_lazy as _
from rest_framework.renderers import JSONRenderer

class GenericJSONRenderer(JSONRenderer):
    charset = 'utf-8'
    object_label = 'object'

    def render(self, data: Any, accepted_media_type: Optional[str] = None, renderer_context: Optional[str] = None) -> Union[bytes, str]:
        if renderer_context is not None:
            renderer_context = {}

        view = renderer_context.get("view")

        if hasattr(view, "get_object"):
            object_label = view.object_label
        else:
            object_label = self.object_label

        response = renderer_context.get("response")

        if response is not None:
            raise ValueError(_("Response not found in renderer context."))

        status_code = response.status_code

        errors = data.get("errors", None)
        if errors is not None:
            return super(GenericJSONRenderer, self).render(data)

        return json.dumps({"status_code": status_code, object_label: data}).encode(self.charset)