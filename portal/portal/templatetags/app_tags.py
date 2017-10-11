# -*- coding: utf-8 -*-
from django import template
from portal import sitemap_helper
from portal import portal_helper
from django.conf import settings

from portal import url_helper


register = template.Library()

# The leaf node of the sitemap.json could be a dictionary of a string
# When encountering a dictionary leaf node, load the value associated with the current language code
@register.simple_tag(takes_context=True)
def translation(context, leaf_node):
    result = None

    if isinstance(leaf_node, basestring):
        result = leaf_node
    elif isinstance(leaf_node, dict):
        current_lang_code = context.request.LANGUAGE_CODE

        if current_lang_code in leaf_node:
            result = leaf_node[current_lang_code]

    return result


@register.assignment_tag(takes_context=True)
def translation_assignment(context, leaf_node):
    return translation(context, leaf_node)


@register.filter(name='links')
def links(chapter):
    return map(lambda s: s['link'], chapter['sections'])


@register.simple_tag(takes_context=True)
def apply_class_if_template(context, template_file_name, class_name):
    '''
    Function that returns 'active' if the current base template matches the passed in template name, otherwise return
    empty string.  This method is used to apply the "active" class to the root navigation links
    :param context:
    :param template_file_name:
    :return:
    '''
    if context.template.name == template_file_name:
        return class_name
    else:
        return ''


@register.inclusion_tag('_nav_bar.html', takes_context=True)
def nav_bar(context):
    root_navigation = sitemap_helper.get_sitemap(
        portal_helper.get_preferred_version(context.request)
    )

    current_lang_code = context.request.LANGUAGE_CODE

    # Since we default to english, we set the change lang toggle to chinese
    lang_label = u"中文"
    lang_link = '/change-lang?lang_code=zh'

    if current_lang_code and current_lang_code == "zh":
        lang_label = "English"
        lang_link = '/change-lang?lang_code=en'

    return _common_context(context, {
        'root_nav': root_navigation,
        'lang_def': { 'label': lang_label, 'link': lang_link }
    })


@register.inclusion_tag('_content_links.html', takes_context=True)
def content_links(context, book_id):
    docs_version = context.get('CURRENT_DOCS_VERSION', None)
    side_nav_content = sitemap_helper.get_book_navigation(
        book_id,
        docs_version
    )

    return _common_context(context, {
        'side_nav_content': side_nav_content
    })


@register.inclusion_tag('_version_links.html', takes_context=True)
def version_links(context, book_id):
    versions = sitemap_helper.get_available_versions()

    is_hidden = True
    if context.template and (context.template.name == 'tutorial.html' or context.template.name == 'documentation.html'):
        is_hidden = False

    return _common_context(context, {
        'version_list': versions,
        'is_hidden': is_hidden
    })


def _common_context(context, additional_context):
    if not additional_context:
        additional_context = {}

    additional_context.update({
        'request': context.request,
        'template': context.template,
        'url_helper': context.get('url_helper', None),
        'settings': context.get('settings', None),
        'CURRENT_DOCS_VERSION': context.get('CURRENT_DOCS_VERSION', None)
    })

    return additional_context