from django import template
from django.utils.safestring import mark_safe
register = template.Library()


@register.simple_tag
def render_input_text(form, field, label, value):

    required, required_span = '', ''
    if form.fields[field].required:
        required = 'required'
        required_span = '<span class="required">*</span>'

    error_class, error_tag = '', ''
    if form[field].errors:
        error_class = 'bad'
        error_tag = '<div class="alert col-md-2 col-sm-2">{}</div>'.format(
            form[field].errors[-1])

    return mark_safe("""
    <div class="item form-group {5}">
      <label class="control-label col-md-3 col-sm-3 col-xs-12"
        for="id_{0}">{1} {4}
        </label>
        <div class="col-md-6 col-sm-6 col-xs-12">
          <input type="text" id="id_{0}" {3} value="{2}"
                name="{0}" value="{{form.instance.name}}"
                class="form-control col-md-7 col-xs-12">
          </select>
        </div>
        {6}
    </div>
    """.format(field, label, value, required, required_span, error_class,
               error_tag))


@register.simple_tag
def render_input_select_m(form, field, label, value):
    options = ''
    for k, v in form.fields[field].choices:
        if k in value:
            options += """
                <option value="{}" selected>{}</option>""".format(k, v)
        else:
            options += """
                        <option value="{}">{}</option>""".format(k, v)

    required, required_span = '', ''
    if form.fields[field].required:
        required = 'required'
        required_span = '<span class="required">*</span>'

    error_class, error_tag = '', ''
    if form[field].errors:
        error_class = 'bad'
        error_tag = '<div class="alert col-md-2 col-sm-2">{}</div>'.format(
            form[field].errors[-1])

    return mark_safe("""
    <div class="item form-group {5}">
      <label class="control-label col-md-3 col-sm-3 col-xs-12"
        for="id_{0}">{1} {3}
        </label>
        <div class="col-md-6 col-sm-6 col-xs-12">
          <select id="id_{0}" name="{0}" {2} multiple
                  class="form-control col-md-7 col-xs-12 select2_single">
            {4}
          </select>
        </div>
        {6}
    </div>
    """.format(field, label, required, required_span, options, error_class,
               error_tag))


@register.simple_tag
def render_input_select(form, field, label, value):
    options = ''
    for k, v in form.fields[field].choices:
        if k == value:
            options += """
                <option value="{}" selected>{}</option>""".format(k, v)
        else:
            options += '<option value="{}">{}</option>'.format(k, v)

    required, required_span = '', ''
    if form.fields[field].required:
        required = 'required'
        required_span = '<span class="required">*</span>'

    error_class, error_tag = '', ''
    if form[field].errors:
        error_class = 'bad'
        error_tag = '<div class="alert col-md-2 col-sm-2">{}</div>'.format(
            form[field].errors[-1])

    return mark_safe("""
    <div class="item form-group {5}">
      <label class="control-label col-md-3 col-sm-3 col-xs-12"
        for="id_{0}">{1} {3}
        </label>
        <div class="col-md-6 col-sm-6 col-xs-12">
          <select id="id_{0}" name="{0}" {2}
                  class="form-control col-md-7 col-xs-12 select2_single">
            {4}
          </select>
        </div>
        {6}
    </div>
    """.format(field, label, required, required_span, options, error_class,
               error_tag))


@register.simple_tag
def render_inline_form_tb(form):
    row = ''
    for field in form:
        field_type = field.field.__class__.__name__
        field_value = field.value() or ''

        required = ''
        if field_value and field.field.required:
            required = 'required'

        # if field.is_hidden:
        #     row += '<input type="hidden" id="id_{0}" name="{0}" ' \
        #            'value= "{1}">'.format(field.html_name, field_value)
        if field_type == 'CharField':
            row += """
                <td><input type="text" id="id_{0}" name="{0}" {1}
                    class="form-control" value= "{2}"></td>
            """.format(field.html_name, required, field_value)
        elif field_type == 'BooleanField':
            row += '<td><input type="checkbox" id="id_{0}" name="{0}" ' \
                   'class="flat"></td>'.format(field.html_name)
        elif field_type in ['ChoiceField', 'TypedChoiceField']:
            options = '<option></option>'
            for k, v in field.field.choices:
                if k == field_value:
                    options += '<option value="{}" selected>{}' \
                               '</option>'.format(k, v)
                else:
                    options += '<option value="{}">{}</option>'.format(k, v)
            row += """
                <td><select id="id_{0}" name="{0}" {1}
                    class="form-control select2_single">
                    {2}
                </select></td>
            """.format(field.html_name, required, options)

    return mark_safe(row)
