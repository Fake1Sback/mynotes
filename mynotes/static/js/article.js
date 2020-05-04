var converter = new showdown.Converter();
converter.setOption('tables', true);
converter.setOption('tasklists', true);
converter.setOption('strikethrough',true);
converter.setOption('backslashEscapesHTMLTags',true);
//converter.setOption('simpleLineBreaks',true);

function Convert(){
  var initial = $('#main-content');
  var initialHTML = initial.html().replace(/&gt;/g,'>').replace(/&lt;/g,'<').replace(/&amp;/g,'&');
  initial.html(converter.makeHtml(initialHTML));
}

function Highlight(){
  $('pre code').each((_,block)=>{
    hljs.highlightBlock(block);
  });
}

$(function(){ 
  
  $('#download-btn').on('click',function(){
    var content = $('#main-content').html();
    $('#conte').val($('#main-content').html());
    $('#Download-form').submit();
  });

  Convert();
  Highlight();
});

