..
  class.rst

{{ fullname | escape | underline }}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
    :members:
    :special-members: __call__
    :show-inheritance:
    :inherited-members:

    {% block attributes %}
        {% if attributes %}
            .. rubric:: {{ _('Attributes') }}

            .. autosummary::
                {% for item in attributes %}
                    ~{{ name }}.{{ item }}
                {%- endfor %}
        {% endif %}
    {% endblock %}

    {% block methods %}
        {% if methods %}
            .. rubric:: {{ _('Methods') }}

            .. autosummary::
                :nosignatures:
                
                {% for item in all_methods %}
                    {%- if not item.startswith('_') or item in ['__init__',
                                                                '__call__'] %}
                    ~{{ name }}.{{ item }}
                    {%- endif -%}
                {%- endfor %}
        {% endif %}
    {% endblock %}