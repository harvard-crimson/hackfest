from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hackserver.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('hackserver.regconfirm.views',
    url(r'^confirm-reg/$', 'confirm_reg', name='confirm_reg'),
)