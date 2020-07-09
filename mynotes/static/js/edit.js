var converter = new showdown.Converter();
converter.setOption('tables', true);
converter.setOption('tasklists', true);
converter.setOption('strikethrough',true);
converter.setOption('backslashEscapesHTMLTags',true);
//converter.setOption('simpleLineBreaks',true);

var firstInput = $('#first');
var secondInput = $('#second');
var cont = $('#cont');
var datalist = $('#tags_datalist')[0];
var textArea = $('#initialText');
var imageUploadCounter = 0;

var key_array = null;
var iv_array = null;

function Convert() {
	var mrkdwn = textArea.val();
	var result = converter.makeHtml(mrkdwn);
	$('#result').html(result);

	$('pre code').each((_, block) => {
		hljs.highlightBlock(block);
	});
}

function SetExternalKey(key_arr,iv_arr,key_name){
	key_array = key_arr;
	iv_array = iv_arr;
	$('#encrypted').prop('checked',true);
	$('#rem-key').css('display','block');
	$('#key-label').css('display','none');
	$('#key-name').html(key_name);
}

function GenerateRandomString(length){
	var characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
	var charactersLength = characters.length
	var result = '';

	for (var i = 0;i < length;i++){
		result += characters.charAt(Math.floor(Math.random() * charactersLength)); 
	}

	return result;
}

$(function () {
	textArea.on('input', function () {
		Convert();
	});

	$('#key-file').on('change',function(){
		var file = $('#key-file')[0].files[0];
		var reader = new FileReader();
		reader.onload = function(){
			var file_content = this.result.split(' ');
			if (file_content.length === 3){
				try
				{
					var key = file_content[0];
					var iv = file_content[1];
					var file_hash = file_content[2];
					var hash = CryptoJS.SHA256(key + iv);

					if (CryptoJS.enc.Hex.stringify(hash) !== file_hash){
						key_array = null;
						iv_array = null;

						$('#key-name').css('color','#d9534f');
						$('#key-name').html('Key is not valid');
						setTimeout(function () {
							$('#key-name').css('color','#212529');
							$('#key-name').html('No Key');
						}, 5000);
						$('#key-file').val('');
						return;
					}

				
					key_array = CryptoJS.enc.Hex.parse(key);
					iv_array = CryptoJS.enc.Hex.parse(iv);
		
					var testString = GenerateRandomString(16);
					var testEncryptedString = CryptoJS.AES.encrypt(testString,key_array,{iv:iv_array});
					var testDecryptedString = CryptoJS.AES.decrypt(testEncryptedString,key_array,{iv:iv_array}).toString(CryptoJS.enc.Utf8);
	
					if (testString === testDecryptedString){
						$('#encrypted').prop('checked',true);			
						$('#key-name').html($('#key-file')[0].files[0].name);
			
						$('#key-label').css('display','none');
						$('#rem-key').css('display','block');

						$('#key-name').css('color','lightgreen');
						setTimeout(function(){
							$('#key-name').css('color','#212529');
						},5000);
					}
					else
					{
						key_array = null;
						iv_array = null;

						$('#key-name').css('color','#d9534f');
						$('#key-name').html('Key is not valid');
						setTimeout(function () {
							$('#key-name').css('color','#212529');
							$('#key-name').html('No Key');
						}, 3000);
						$('#key-file').val('');
					}
				}
				catch(error){
					key_array = null;
					iv_array = null;

					$('#key-name').css('color','#d9534f');
					$('#key-name').html('Key is not valid');
					setTimeout(function () {
						$('#key-name').css('color','#212529');
						$('#key-name').html('No Key');
					}, 5000);
					$('#key-file').val('');
				}
			}
			else {
				$('#key-name').css('color','#d9534f');
				$('#key-name').html('Key is not valid');
				setTimeout(function () {
                    $('#key-name').css('color','#212529');
                    $('#key-name').html('No Key');
				}, 5000);
				$('#key-file').val('');
			}
		}

		reader.readAsText(file);
	});

	$('#edit-form').submit(function(){
		if ($('#encrypted').prop('checked') === true && key_array != null && iv_array != null){
			textArea.val(CryptoJS.AES.encrypt(textArea.val(),key_array,{iv: iv_array}));
			return true;
		}
		else if ($('#encrypted').prop('checked') === false && key_array == null && iv_array == null){
			return true;
		}
		else{
			return false;
		}
	});

	$('#rem-key').on('click',function(){
		key_array = null;
		iv_array = null;
		$('#encrypted').prop('checked',false);

		$('#key-name').html('No Key');
		$('#rem-key').css('display','none');
		$('#key-label').css('display','block');
	});

	$(document).delegate('#initialText', 'keydown', function(e) {
		var keyCode = e.keyCode || e.which;
	  
		if (keyCode == 9) {
		  e.preventDefault();
		  var start = this.selectionStart;
		  var end = this.selectionEnd;
	  
		  // set textarea value to: text before caret + tab + text after caret
		  $(this).val($(this).val().substring(0, start)
					  + "\t"
					  + $(this).val().substring(end));
	  
		  // put caret at right position again
		  this.selectionStart = start + 1;
		  this.selectionEnd = start + 1;
		}
	  });

	if (datalist != null) {
		var options = datalist.options;
		firstInput.on('input', function () {
			for (var i = 0; i < options.length; i++) {
				if (firstInput.val() === options[i].value) {
					strings = secondInput.val().replace(' ', '').split(',');
					var matchFound = false;

					for (var j = 0; j < strings.length; j++) {
						if (firstInput.val() === strings[j]) {
							matchFound = true;
						}
					}

					if (!matchFound) {
						if (secondInput.val() === '') {
							secondInput.val(secondInput.val() + options[i].value);
						}
						else {
							secondInput.val(secondInput.val() + ',' + options[i].value);
						}

						var str = document.createElement('div');
						var btn = document.createElement('button');
						btn.className = "tag_btn";
						btn.onclick = DeleteTag;
						str.innerHTML = str.innerHTML + options[i].value;
						str.classList.add("tag_div", "badge", "badge-info", "px-2", "py-2", "mr-1");
						str.appendChild(btn);
						cont[0].appendChild(str);
						firstInput.val('');
					}
				}
			}
		});

		function InitialShowTags() {
			var article_tags = secondInput.val();
			article_tags_array = article_tags.split(',');
			for (var i = 0; i < article_tags_array.length; i++) {
				article_tags_array[i].trim();
			}

			for (var i = 0; i < options.length; i++) {
				for (var j = 0; j < article_tags_array.length; j++) {
					if (options[i].value == article_tags_array[j]) {
						var str = document.createElement('div');
						var btn = document.createElement('button');
						btn.className = "tag_btn";
						btn.onclick = DeleteTag;
						str.innerHTML = str.innerHTML + options[i].value;
						str.classList.add("tag_div", "badge", "badge-info", "px-2", "py-2", "mr-1");
						str.appendChild(btn);
						cont[0].appendChild(str);
						firstInput.val('');
					}
				}
			}
		}

		InitialShowTags();
	}

	function DeleteTag(e) {
		var text_to_remove = e.target.parentNode.firstChild.data;
		var input_2_strings = secondInput.val().split(',');
		for (var i = 0; i < input_2_strings.length; i++) {
			input_2_strings[i].trim();
		}
		var new_str = "";
		for (var i = 0; i < input_2_strings.length; i++) {
			if (input_2_strings[i] !== text_to_remove) {
				if (new_str === "") {
					new_str = input_2_strings[i];
				}
				else {
					new_str = new_str + ',' + input_2_strings[i];
				}
			}
		}
		secondInput.val(new_str);
		e.target.parentNode.remove();
	}

	$('#url-download').on('change', function (e) {
		var file = e.target.files[0];
		temporary_id = $('#temporary_id').val();
		article_id = $('#art-id-hidden').val();
		var formData = new FormData();

		if (temporary_id && article_id == null) {
			formData.append('temp-id', temporary_id);
		}
		else if (!temporary_id && article_id != null) {
			formData.append('art-id', article_id);
		}
		formData.append('article-image', file);

		$.ajax({
			url: '/articleimage',
			type: 'POST',
			data: formData,
			processData: false,
			contentType: false,
			success: function (result) {
				imageUploadCounter += 1;
				var hiddenInput = $('#hiddenp');
				hiddenInput.val('[Image Name ' + imageUploadCounter.toString() + ']:' + result);
				hiddenInput[0].select();
				document.execCommand('copy');
				hiddenInput.value = '';

				var desc = $('#url_desc');
				desc.text('COPY: ' + '[Image Name ' + imageUploadCounter.toString() + ']:' + result);
				desc.removeClass('text-muted');
				desc.addClass('text-success');
				setTimeout(function () {
					desc.text('Upload image on server and get the url into clipboard');
					desc.removeClass('text-success');
					desc.addClass('text-muted');
				}, 10000);
			},
			error: function () {
				var desc = $('#url_desc');
				desc.text('File upload failed. Try again later');
				desc.removeClass('text-muted');
				desc.addClass('text-danger');
				setTimeout(function () {
					desc.text('Upload image on server and get the url into clipboard');
					desc.removeClass('text-danger');
					desc.addClass('text-muted');
				}, 5000);
			}
		});
	});

	$('#download').on('change', function (e) {
		var reader = new FileReader();

		reader.onloadend = function () {
			imageUploadCounter += 1;
			var imageBase64String = this.result;
			var hiddenInput = $('#hiddenp');
			hiddenInput.val('[Image Name ' + imageUploadCounter.toString() + ']:' + imageBase64String);
			hiddenInput[0].select();
			document.execCommand('copy');
			hiddenInput.value = '';

			var desc = $('#base64_desc');
			desc.text('Base64 image is in clipboard. Paste it to the article.');
			desc.removeClass('text-muted');
			desc.addClass('text-success');
			setTimeout(function () {
				desc.text('Get the base64 representation of image into clipboard');
				desc.removeClass('text-success');
				desc.addClass('text-muted');
			}, 5000);
		}

		reader.onerror = function () {
			var desc = $('#base64_desc');
			desc.text('Converting file to base64 failed. Try again later');
			desc.removeClass('text-muted');
			desc.addClass('text-danger');
			setTimeout(function () {
				desc.text('Get the base64 representation of image into clipboard');
				desc.removeClass('text-danger');
				desc.addClass('text-muted');
			}, 5000);
		}

		reader.readAsDataURL(e.target.files[0]);
	});

	function UpdateUploadCounter() {
		var initText = $('#initialText').val();
		var pattern = /\[(Image) (Name) \d*\]/g;
		var n = initText.match(pattern);
		var newN = Array.from(new Set(n));

		for (var i = 0; i < newN.length; i++) {
			var tempStr = newN[i].split(' ');
			var number = parseInt(tempStr[tempStr.length - 1].replace(']', ''), 10);

			if (!isNaN(number)) {
				if (number > imageUploadCounter) {
					imageUploadCounter = number;
				}
			}
		}

		if (imageUploadCounter == null || isNaN(imageUploadCounter)) {
			imageUploadCounter = 0;
		}
	}

	Convert();
	UpdateUploadCounter();
});
