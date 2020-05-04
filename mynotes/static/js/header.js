$(function(){
    var navigation_menu = $('#nav_menu');

    $('#collapseButton').on('click',function(){
        if (navigation_menu.css('display') === 'none'){
            navigation_menu.slideDown(500);
        }
        else
        {
            navigation_menu.slideUp(500,function(){
                navigation_menu.removeAttr('style');
            });
        }
    });

    $(window).resize(function(){
        if(window.outerWidth > 768){
                navigation_menu.removeAttr('style');
        }
    });
    
    $('.del-item-button').on('click',function(e){
        var del_confirm = $(this).parent().next();
        if(del_confirm.css('display') === 'none'){
            $(this).parent().next().css('display','block');
        }
        else
        {
            del_confirm.css('display','none');
        }
    });
    
    $('.abort-del').on('click',function(e){
        $(this).parent().css('display','none');
    });
    
    $('#search-container-btn').on('click',function(e){
        var search_container = $('#search-container');
        if (search_container.css('display') == 'none'){
            search_container.css('display','block');
            $(this)[0].innerHTML = "Close";
        }
        else
        {
            search_container.css('display','none');
            $(this)[0].innerHTML = "Search";
        }
    });
    
    $('.special-submit').on('click',function(){
        $('.new-prepand-flex').each(function(){
            if($(this)[0].hasAttribute('required') && $(this).val().replace(' ','') === '')
            {
               $(this).parent().attr('style','border-color:red;box-shadow:0px 0px 4px 1px red;');
            }
        });
    });
    
    $('.new-prepand-flex').on('input',function(){
        $(this).parent().removeAttr('style');
    });
});

