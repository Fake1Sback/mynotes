function GenerateRandomString(length){
	var characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
	var charactersLength = characters.length
	var result = '';

	for (var i = 0;i < length;i++){
		result += characters.charAt(Math.floor(Math.random() * charactersLength)); 
	}

	return result;
}

$(function(){
    var key_array = null;
    var iv_array = null;
    var file = null;

    $('#add-key-input').on('change',function(e){
        file = e.target.files[0];
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

                    if (file_hash !== CryptoJS.enc.Hex.stringify(hash)){
                        key_array = null;
                        iv_array = null;

                        showMessage('Key is not valid','No Key',5000);
                        return;
                    }

                    key_array = CryptoJS.enc.Hex.parse(key);
                    iv_array = CryptoJS.enc.Hex.parse(iv);

                    var testString = GenerateRandomString(16);

                    var testEncryptedString = CryptoJS.AES.encrypt(testString,key_array,{iv:iv_array});

                    var testDecryptedString = CryptoJS.AES.decrypt(testEncryptedString,key_array,{iv:iv_array}).toString(CryptoJS.enc.Utf8);

                    if (testString === testDecryptedString){
                        $('#add-key-name').html($('#add-key-input').val().split('\\').pop());
                        $('#add-key-name').css('color','lightgreen');
                        setTimeout(function(){
                            $('#add-key-name').css('color','#212529');
                        }, 3000);
                    }
                    else{
                        key_array = null;
                        iv_array = null;

                        showMessage('Key is not valid','No Key',5000);
                    }
                }
                catch(error){
                    key_array = null;
                    iv_array = null;
                    showMessage('Key is not valid','No Key',5000);
                }   
            }
            else
            {
                showMessage('Key is not valid','No Key',5000);
            }
        };

        reader.onerror = function(){
            showMessage('File read error','No Key',5000);
        }

        reader.readAsText(e.target.files[0]);
    });

    $('#add-decrypt-btn').on('click',function(){
        try
        {
            var encryptedArticle = $('#add-encrypted-content').val();
            var decryptedContent = CryptoJS.AES.decrypt(encryptedArticle,key_array,{iv:iv_array}).toString(CryptoJS.enc.Utf8);
            if (decryptedContent !== '')
            {
                var el = document.getElementById('middleLine');

                if (el == null){
                    ArticlePageFunc(decryptedContent);
                }
                else
                {
                    EditPageFunc(decryptedContent);
                }
            }
            else{
                showMessage('Decryption Failed','No Key',5000);
            }
        }
        catch(e){
            showMessage('Decryption Failed','No Key',5000);
        }
    });

    function showMessage(firstMessage,secondMessage,miliseconds){
        $('#add-key-input').val('');
        $('#add-key-name').css('color','red');
        $('#add-key-name').html(firstMessage);
        setTimeout(function () {
            $('#add-key-name').css('color','#212529');
            $('#add-key-name').html(secondMessage);
        }, miliseconds);
    }

    function EditPageFunc(decryptedContent){
        $('.article-edit-container').removeAttr('style');
        $('.caption').removeAttr('style');
        $('#key-managment-div').css('display', 'none');
        $('#initialText').val(decryptedContent);

        Convert();
        SetExternalKey(key_array, iv_array, file.name)
    }

    function ArticlePageFunc(decryptedContent){
        $('#main-div').removeAttr('style');
        $('#key-managment-div').css('display','none');
        $('#main-content').html(decryptedContent);

        Convert();
        Highlight();
    }
});