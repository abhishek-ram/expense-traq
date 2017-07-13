from django import template
from django.utils.safestring import mark_safe
from ast import literal_eval

register = template.Library()


@register.simple_tag
def render_input_text(field, label=None):
    field_type = field.field.__class__.__name__
    field_value = field.value() or ''

    required, required_span = '', ''
    if field.field.required:
        required = 'required'
        required_span = '<span class="required">*</span>'

    error_class, error_tag = '', ''
    if field.errors:
        error_class = 'bad'
        error_tag = '<div class="alert col-md-2 col-sm-2">{}</div>'.format(
            field.errors[-1])

    input_type = 'type="text"'
    if field_type == 'DecimalField':
        input_type = 'type="number" step="0.01"'

    return mark_safe("""
        <div class="item form-group {6}">
          <label class="control-label col-md-3 col-sm-3 col-xs-12"
            for="id_{0}">{2} {5}
            </label>
            <div class="col-md-6 col-sm-6 col-xs-12">
              <input {1} id="id_{0}" {4} value="{3}"
                    name="{0}" value="{{form.instance.name}}"
                    class="form-control col-md-7 col-xs-12">
              </select>
            </div>
            {7}
        </div>
        """.format(field.html_name, input_type, label or field.label,
                   field_value, required, required_span, error_class,
                   error_tag))


@register.simple_tag
def render_input_select(field, label=None, select2=True):
    field_type = field.field.__class__.__name__
    field_values = [str(field.value() or '')]

    multiple,  = '',
    if 'Multiple' in field_type:
        multiple = 'multiple'
        field_values = [str(v) for v in literal_eval(field.value() or '[]')]

    options = ''
    for k, v in field.field.choices:
        if str(k) in field_values:
            options += """
                <option value="{}" selected>{}</option>""".format(k, v)
        else:
            options += '<option value="{}">{}</option>'.format(k, v)

    required, required_span = '', ''
    if field.field.required:
        required = 'required'
        required_span = '<span class="required">*</span>'

    error_class, error_tag = '', ''
    if field.errors:
        error_class = 'bad'
        error_tag = '<div class="alert col-md-2 col-sm-2">{}</div>'.format(
            field.errors[-1])

    select_class = 'select2_single' if select2 else ''
    return mark_safe("""
    <div class="item form-group {6}">
      <label class="control-label col-md-3 col-sm-3 col-xs-12"
        for="id_{0}">{1} {4}
        </label>
        <div class="col-md-6 col-sm-6 col-xs-12">
          <select id="id_{0}" name="{0}" {2} {3}
                  class="form-control col-md-7 col-xs-12 {8}">
            {5}
          </select>
        </div>
        {7}
    </div>
    """.format(field.html_name, label or field.label, multiple, required,
               required_span, options, error_class, error_tag, select_class))


@register.simple_tag
def render_inline_form_tb(form):
    row = ''
    for field in form:
        field_type = field.field.__class__.__name__
        field_value = field.value() or ''

        required = ''
        if field_value and field.field.required:
            required = 'required'

        error_tag = '', ''
        if field.errors:
            error_tag = 'data-toggle="error-tooltip" title="{}"'.format(
                field.errors[-1])

        if field.is_hidden:
            pass
        elif field_type == 'CharField':
            row += """
                <td><input type="text" id="id_{0}" name="{0}" {1}
                    class="form-control" value= "{2}" {3}></td>
            """.format(field.html_name, required, field_value, error_tag)
        elif field_type == 'DecimalField':
            row += """
                <td><input type="number" step="0.01" id="id_{0}" name="{0}" {1}
                    class="form-control has-error" value= "{2}" {3}></td>
            """.format(field.html_name, required, field_value, error_tag)
        elif field_type == 'BooleanField':
            row += '<td><input type="checkbox" id="id_{0}" name="{0}" ' \
                   'class="flat"></td>'.format(field.html_name)
        elif 'ChoiceField' in field_type:
            options = ''
            for k, v in field.field.choices:
                if str(k) == str(field_value):
                    options += '<option value="{}" selected>{}' \
                               '</option>'.format(k, v)
                else:
                    options += '<option value="{}">{}</option>'.format(k, v)
            row += """
                <td><select id="id_{0}" name="{0}" {1} {3}
                    class="form-control select2_single">
                    {2}
                </select></td>
            """.format(field.html_name, required, options, error_tag)

    return mark_safe(row)
