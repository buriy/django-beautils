from blocks import make_source
from bparser import get_blocks_and_errors
from test_admin import test_create_with_admin
from views import render_test
import assets #@UnusedImport
import utils #@UnusedImport

def test_hardparse():
    blocks, errors = get_blocks_and_errors(u"""
        {% widget demo/keywords news44=false var="greetings" %}<br/>
        {% image "/media/images/Cities.com_Logo_Green.png" %}<br/>
        {% set ppp="lings" %}
        {% set zzz:image="/media" %}
        {% hide zzz %}
        {% set ttt %}
        hello earth{{ ppp }}!
        {% endset %}
        {{ ttt }}
    """, debug=True)
    assert errors == [], errors
    assert blocks
    assert blocks['ppp'].type == 'html'
    assert blocks['ppp'].hidden
    assert blocks['ttt'].value == 'hello earth{{ ppp }}!'
    print "PASSED"

def test_hardparse2():
    blocks, errors = get_blocks_and_errors(u"""
{% section "Business" as business %}
{% link business "money" as money %}
<br>Result: {{ money }}
<br>Alt: {{ money.alt }}
<br>Url: {{ money.url }}
<br>Name: {{ money.name }}
<br>Link:
<a href="{{ money.url }}" alt="{{ money.name }}">{{ money.title }}</a>
    """, debug=True)
    assert errors == [], errors
    assert blocks
    print "PASSED"

def test_links_work():
    template = """
{% section "Business" as business %}
{% link business "money" as money %}
<a href="{{ money.url }}" alt="{{ money.name }}">{{ money.title }}</a>
    """
    src = render_test(template).content
    assert src.strip() == """<a href="http://money.wn.com/" alt="money">Money</a>""", src.strip()
    print "PASSED"

def test_reparse():
    template = u"""
{% extends "includes/chiefengineer_style.html" %}
{% set head_title="Page title" %}
{% set testvar=true %}
{% section "Business" as mysection %}
{% set abc="Business" %}
{% section abc as supersection %}
{% set loop %}[[aa||[[dd||bb]]||cc||dd]]{% endset %}
{% block meta_description %}{% link supersection "myname" as li %}Employment opportunities....{% endblock %}
{% block meta_keywords %}Employment opportunities for ...{% endblock %}
{% block logo %}<a href="http://www.page_url.com/" title="Page title"><img src="/media/chiefengineer_style/images/logo.png" width="970" height="72" border="0" alt="Page title" title="Page title" /></a>{% endblock %}
{% block email %}charter@barges.com{% endblock %}
{% block employment_content %}<iframe src="http://newerforms.wn.com/form/marine_electricians/" height="840" width="600" marginheight="0" marginwidth="0" frameborder="0" scrolling="Auto" ></iframe>{% endblock %}
""".strip()
    blocks, errors = get_blocks_and_errors(template, debug=True)
    assert errors == [], errors
    assert blocks
    source = make_source("includes/chiefengineer_style.html", blocks)
    slen = len(source.split('\n'))
    tlen = len(template.split('\n'))
    assert slen == tlen, "%s != %s\n%s" % (slen, tlen, source)
    for sl, tl in zip(source.split('\n'), template.split('\n')):
        if sl != tl: print "%s != %s" % (sl, tl)
    print "PASSED"

def test_simple():
    blocks, errors = get_blocks_and_errors(u"""
        {% if testvar %}{% for n,v in loop %}
        {% for k in n %}{% endfor %}
        {% endfor %}{% endif %}
    """, debug=True)
    assert errors == [], errors
    assert blocks
    print "PASSED"

def test_ignore():
    blocks, errors = get_blocks_and_errors(u"""
        <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />  
                <title>{% block head_title %}Page title{% endblock %}</title>
        {% if testvar %}{% for n,v in loop %}
                <meta name="description" content="{% block meta_description %}Employment opportunities....{% endblock %}" />
                {% for k in n %}{% endfor %}
        {% endfor %}{% endif %}
                <meta name="keywords" content="{% block meta_keywords %}Employment opportunities for ...{% endblock %}" />
                <link rel="shortcut icon" href="/media/chiefengineer_style/images/favicon.ico" type="image/x-icon" />
                   <link href="/media/chiefengineer_style/css/styles.css" rel="stylesheet" type="text/css" /> 
            </head>
            
            
        <body>
            
              <!-- The header -->
              <div id="header">
                  {% block logo %}
                  <a href="http://www.page_url.com/" title="Page title"><img src="/media/chiefengineer_style/images/logo.png" width="970" height="72" border="0" alt="Page title" title="Page title" /></a>
                {% endblock %}</div>
              </div>
              <!-- Header ends -->
              
        
        <div id="container">        
                    
                <!-- tdnavbar: start -->
                <div id="tdnavbar">
                    <ul class="tdnavbar">
                        <li><a href="index.html" class="active">Employment</a></li>                
                        <li><a href="activities.html">Activities</a></li>
                        <li><a href="http://rss.wn.com/English/keyword/Maritime">Offshore News</a></li>                
                        <li><a href="http://www.barges.com/">Vessels / Barges</a></li>                    
                        <li><a href="aboutus.html">About us</a></li>                    
                        <li><a href="mailto:{% block email %}charter@barges.com{% endblock %}">E-mail us</a></li>
                    </ul>        
                </div>
                <!-- tdnavbar: end -->
                
                
                <div id="body">
                    {% block content %}
                        <div class="content employment">
                                
                            
                        <br clear="all" />
                        
                        {% block employment_content %}
                                <iframe src="http://newerforms.wn.com/form/marine_electricians/" height="840" width="600" marginheight="0" marginwidth="0" frameborder="0" scrolling="Auto" ></iframe>
                        {% endblock %}
                  
                  
                        </div>
                    {% endblock %}
                    
                </div>
                <!-- body ends -->    
                
                
                <div id="bottom_bgr"></div>
                
                
                <div id="bottom_bar">
                    <div class="content">Copyright &copy; 2008</div>
                
                </div>
         </div>
        <!-- Container ends -->    
                
            
         
         </body>
         </html>
    """, debug=True)
    assert errors == [], errors
    assert 'loop' in blocks and not 'n' in blocks
    print "PASSED"

def test_make_source():
    blocks, errors = get_blocks_and_errors(u"""
<html>
    <head>
        <title>{{ page_title }}</title>
        <meta name="description" content="{{ meta_description }}" />            
        <meta name="keywords" content="{{ meta_keywords }}" />
        
        <meta name="robots" content="index,follow" />
        <link rel="stylesheet" href="{% media /media/health/css/styles2.css %}" />
        <link rel="SHORTCUT ICON" href="{% media /media/health/images/favicon.ico %}" type="image/x-icon" />
        <style type="text/css">
        div#menu ul li a.{{ section_name }}
        {
            background-color: #ff6600 !important;
        }
        ul#menu_ads li a.{{ section_name }}{
            background: #FF6600;
        }
        </style>
    </head>
        
    <body>
        
    <!-- The header -->
    <div id="header">
        <div class="content">
        
            <a href="http://www.wn.com/health" class="logo"></a>
            
            <div id="spons_text">Sponsored Links</div>
            
            <div id="search">
                        <form id="form-search" action="http://upge.wn.com/" accept-charset="utf-8" method="GET">
                        <input type="text" name="query" value="search WN for News" maxlength="8192" class="top_query" />
                        <input type="hidden" name="version" value="1" />
                        <input type="hidden" name="template" value="cheetah-search/index.txt" />
                        <input type="Image" src="{% media /media/images/search.gif %}" class="search" />                                                
                        </form>
            </div>              
            <ul id="top_links">                         
                <li><a href="http://www.wnnmedia.com/contact.html">Contact</a></li>                                             
                <li><a href="http://forms.wn.com/form/advertising-enquiry/">Advertise with us</a></li>                                          
                <li><a href="http://forms.wn.com/form/wn-feedback/">Feedback</a></li>                                           
            </ul>               
                                    
        </div>
    </div>
    <!-- The header ends -->                            
                    
    <!-- container -->                  
    <div id="container">                                
            
            <div class="body">  
                
                    <div id="page_title">
                        <ul>
                            <li><img src="{% media /media/health/images/pagetitle_left.png %}" width="3" height="50" alt="{{ page_title }}" title="{{ page_title }}" /></li>
                            <li class="text"><div style="margin-top: 10px;"><a href="{{ page_url }}">{{ page_title }}</a></div></li>
                            <li><img src="{% media /media/health/images/pagetitle_right.png %}" width="3" height="50" alt="{{ page_title }}" title="{{ page_title }}" /></li>
                        </ul>
                    </div>      
                    
                    <div id="date">{% now "l j F Y" %}</div>    
                    
                    <div id="menu">
                        <img src="{% media /media/health/images/menu_right_green.png %}" width="15" height="33" alt=""          class="menu_right" />
                        <img src="{% media /media/health/images/menu_left_green.png %}" width="15" height="33" alt="" class="menu_left" />                                              <div class="menu_list">
                        <ul>            
                         <!-- {{ menu_section }} -->
                        {% section menu_section as section %}
                            {% for b in section.link_set.all %}
                                <li><a href="{{ b.url }}" title="{{ b.alt }}" class="{{ b.alt }}">{{ b.name }}</a></li>
                            {% endfor %}
                        
                        </ul>
                        </div>
                    </div>
                
                
                <div id="content">                      
                    {% section menu_section as section %}
                    {% link section "breadcrumb_trail" as breadcrumb_trail %}
                    <a href="{{ breadcrumb_trail.url }}" alt="{{ breadcrumb_trail.name }}">{{ breadcrumb_trail.name }}</a>
                    
                    <div id="leftC">            
                            {% block page_content %}    
                            
                            {% endblock %}
                    </div>      
                                        
                    <div id="rightC">
                        <div class="spons_links">Sponsored Links</div>
                        {% widget list_section section="health_adsites" %}
                        
                        {% if right_column_img %}                                                               
                        <div id="health">
                            <div class="text1">Easy access to health topics.</div>
                            <div class="text2">Find resources for <br />
                            researching <br />
                            illnesses, <br />
                            injuries, <br />
                            medical conditions, <br />
                            diseases,<br />
                            latest health news.</div>
                        </div>
                        {% endif %}
                        
                        <!-- {{ google_keywords }}  -->                         
                        
                        {% if google_mpu_1 %}
                            
<script type='text/javascript'><!--//<![CDATA[
   var m3_u = (location.protocol=='https:'?'https://phpadsnew.wn.com/www/delivery/ajs.php':'http://phpadsnew.wn.com/www/delivery/ajs.php');
   var m3_r = Math.floor(Math.random()*99999999999);
   if (!document.MAX_used) document.MAX_used = ',';
   document.write ("<scr"+"ipt type='text/javascript' src='"+m3_u);
   document.write ("?zoneid=227");
   document.write ('&amp;cb=' + m3_r);
   if (document.MAX_used != ',') document.write ("&amp;exclude=" + document.MAX_used);
   document.write ("&amp;loc=" + escape(window.location));
   if (document.referrer) document.write ("&amp;referer=" + escape(document.referrer));
   if (document.context) document.write ("&context=" + escape(document.context));
   if (document.mmm_fo) document.write ("&amp;mmm_fo=1");
   document.write ("'><\/scr"+"ipt>");
//]]>--></script><noscript><a href='http://phpadsnew.wn.com/www/delivery/ck.php?n=a5164cf8&amp;cb=INSERT_RANDOM_NUMBER_HERE' target='_blank'><img src='http://phpadsnew.wn.com/www/delivery/avw.php?zoneid=227&amp;cb=INSERT_RANDOM_NUMBER_HERE&amp;n=a5164cf8' border='0' alt='' /></a></noscript>


                        {% endif %}
                        
                        {% if google_mpu_2 %}
                            
<script type='text/javascript'><!--//<![CDATA[
   var m3_u = (location.protocol=='https:'?'https://phpadsnew.wn.com/www/delivery/ajs.php':'http://phpadsnew.wn.com/www/delivery/ajs.php');
   var m3_r = Math.floor(Math.random()*99999999999);
   if (!document.MAX_used) document.MAX_used = ',';
   document.write ("<scr"+"ipt type='text/javascript' src='"+m3_u);
   document.write ("?zoneid=227");
   document.write ('&amp;cb=' + m3_r);
   if (document.MAX_used != ',') document.write ("&amp;exclude=" + document.MAX_used);
   document.write ("&amp;loc=" + escape(window.location));
   if (document.referrer) document.write ("&amp;referer=" + escape(document.referrer));
   if (document.context) document.write ("&context=" + escape(document.context));
   if (document.mmm_fo) document.write ("&amp;mmm_fo=1");
   document.write ("'><\/scr"+"ipt>");
//]]>--></script><noscript><a href='http://phpadsnew.wn.com/www/delivery/ck.php?n=a5164cf8&amp;cb=INSERT_RANDOM_NUMBER_HERE' target='_blank'><img src='http://phpadsnew.wn.com/www/delivery/avw.php?zoneid=227&amp;cb=INSERT_RANDOM_NUMBER_HERE&amp;n=a5164cf8' border='0' alt='' /></a></noscript>

                        {% endif %}                     
                                
                        {% if google_mpu_3 %}
                            
<script type='text/javascript'><!--//<![CDATA[
   var m3_u = (location.protocol=='https:'?'https://phpadsnew.wn.com/www/delivery/ajs.php':'http://phpadsnew.wn.com/www/delivery/ajs.php');
   var m3_r = Math.floor(Math.random()*99999999999);
   if (!document.MAX_used) document.MAX_used = ',';
   document.write ("<scr"+"ipt type='text/javascript' src='"+m3_u);
   document.write ("?zoneid=227");
   document.write ('&amp;cb=' + m3_r);
   if (document.MAX_used != ',') document.write ("&amp;exclude=" + document.MAX_used);
   document.write ("&amp;loc=" + escape(window.location));
   if (document.referrer) document.write ("&amp;referer=" + escape(document.referrer));
   if (document.context) document.write ("&context=" + escape(document.context));
   if (document.mmm_fo) document.write ("&amp;mmm_fo=1");
   document.write ("'><\/scr"+"ipt>");
//]]>--></script><noscript><a href='http://phpadsnew.wn.com/www/delivery/ck.php?n=a5164cf8&amp;cb=INSERT_RANDOM_NUMBER_HERE' target='_blank'><img src='http://phpadsnew.wn.com/www/delivery/avw.php?zoneid=227&amp;cb=INSERT_RANDOM_NUMBER_HERE&amp;n=a5164cf8' border='0' alt='' /></a></noscript>

                        {% endif %}                     
                        
                    </div>                              
                    
                    <br clear="all" />
                </div>
                <!-- div#content ends -->       

        </div>
         <!-- div body ends -->         
         <br clear="all" />     
     </div>
     <!-- div container ends -->
            
            
            
    <!-- bottom starts -->
    <div id="bottom">
        <div class="content">
                <a href="http://www.wnnmedia.com" target="_top">Media Kit</a>
                <a href="http://wntoolbar.com/" target="_top">WN Toolbar</a>
                <a href="http://www.wn.com/languages">Languages</a>
                <a href="http://www.wn.com/employment">Jobs</a>
                <a href="http://asp.wn.com/yourphotos">Submit Photos</a>
                <a href="http://www.wn.com/wnlinks">WN Links</a>
                <a href="http://displays.com">Text Link Ads</a>
                <a href="http://www.wn.com"> &copy; 2009 WN Network</a>
                <br />
                <a href="http://forms.wn.com/form/advertising-enquiry/">Contact our Advertising team for Advertising or Sponsorship on World News Network</a>
        </div>
    </div>      
    <!-- bottom ends -->

    

    </body>
</html>
    """, debug=True)
    assert errors == [], errors
    s = make_source("base.html", blocks)
    assert len(s.split('\n')) == len(blocks)+1
    print "PASSED"

if __name__ == "__main__":
    test_simple()
    test_ignore()
    test_hardparse()
    test_hardparse2()
    test_make_source()
    test_reparse()
    test_links_work()
    test_create_with_admin()

