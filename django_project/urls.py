from django.conf.urls import patterns, include, url
from django_project.api import userApi, dealsApi, merchantApi,redeemCoupon, profileApi, ratingApi
from django_project.merchantApi import getApi, postApi
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'django_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

url(r'^text',redeemCoupon.test,name='redeemCoupon.test'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^perkkx/user/coupon/(?P<uid>\w+)', userApi.user_coupons, name='userApi.user_coupons'),
    url(r'^perkkx/signup', userApi.signup, name='userApi.signup'),
    url(r'^perkkx/user', userApi.getdata, name='userApi.getdata'),
    
    url(r'^perkkx/update/user',userApi.updateuser, name='userApi.updateuser'),
    url('^perkkx/check', userApi.user_exist, name="userApi.user_exist"),
    url(r'^perkkx/echo', 'preks.echo'),
    url(r'^perkkx/verifyUser/(?P<code>\w+)', userApi.verifyUser, name='userApi.verifyUser'),
    url(r'^perkkx/deals/(?P<user>\w+)/(?P<category>\d+)/(?P<typ>\w+)', dealsApi.get_deals, name='dealsApi.get_deals'),
    url(r'^perkkx/deals', dealsApi.get_totals, name='dealsApi.get_totals'),
    url(r'^perkkx/merchant/coupon/(?P<mID>\d+)', merchantApi.get_coupons, name='merchantApi.get_coupons'),
    url(r'^perkkx/getCompany', userApi.getFacility, name='userApi.getFacility'),
    url(r'^perkkx/redeem/check', redeemCoupon.check_coupon, name='redeemCoupon.check_coupon'),
    url(r'^perkkx/redeem', redeemCoupon.add_coupon, name='redeemCoupon.add_coupon'),

    url(r'^perkkx/merchant/(?P<mID>\d+)', merchantApi.merchants, name='merchantApi.merchant'),
    url(r'^perkkx/mfollow/(?P<user>\w+)/(?P<vendor>\d+)', userApi.fMerchant, name='userApi.fMerchant'),

    url(r'^perkkx/profile/savings/(?P<userID>\w+)', profileApi.get_savings, name='profileApi.get_savings'),
    url(r'^perkkx/profile/followed/(?P<userID>\w+)', profileApi.get_followed, name='profileApi.get_followed'),
    url(r'^perkkx/profile/rate', ratingApi.rate_merchant, name='ratingApi.rate_merchant'),
    url(r'^perkkx/profile/check', ratingApi.check_pending, name='ratingApi.check_pending'),
    url(r'^perkkx/profile/ratings', ratingApi.get_ratings, name='ratingApi.get_ratings'),

    url(r'^perkkx/merchantapp/validate', getApi.validate_code, name='getApi.validate_code'),
    url(r'^perkkx/merchantapp/login', postApi.login, name='postApi.login'),
    url(r'^perkkx/merchantapp/signup', postApi.signup, name='postApi.signup'),      # Not to be used by app
    url(r'^perkkx/merchantapp/submit/(?P<vendor_id>\d+)', postApi.post, name='postApi.post'),
    url(r'^perkkx/merchantapp/count/(?P<vendor_id>\d+)', getApi.get_count, name='getApi.get_count'),
    url(r'^perkkx/merchantapp/(?P<typ>\w+)/(?P<vendor_id>\d+)', getApi.get, name='getApi.get')

)
