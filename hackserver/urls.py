from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import RedirectView

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hackserver.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^comp/$', RedirectView.as_view(url='https://docs.google.com/forms/d/1UYQ5Eu30gRtwCel7oERN085Itg3K9-E4IEjS-zYmQqo/viewform'))
)

urlpatterns += patterns('hackserver.regconfirm.views',
    url(r'^confirm/$', 'confirm_reg', name='confirm_reg'),
)
