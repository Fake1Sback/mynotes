function generateKey(passphrase){
    var salt = CryptoJS.lib.WordArray.random(128 / 8);
    var key256bits = CryptoJS.PBKDF2(passphrase,salt,{
        keySize: 256 / 32,
        iterations:500
    });
    var iv128bits = CryptoJS.PBKDF2(passphrase,salt,{
        keySize: 128 / 32,
        iterations:500
    });
    var hash = CryptoJS.SHA256(CryptoJS.enc.Hex.stringify(key256bits) + CryptoJS.enc.Hex.stringify(iv128bits));
    return {
        key: key256bits,
        iv: iv128bits,
        hash: hash
    }
}

$('#keygen').on('click',function(){
    var filename = $('#filename').val();
    console.log(filename);

    var user_input = $('#passphrase').val();
    console.log(user_input);

    if (user_input !== '' && filename !== ''){

        var key_obj = generateKey(user_input);
        console.log('Hash: ' + CryptoJS.enc.Hex.stringify(key_obj.hash))
    
        var file_content = CryptoJS.enc.Hex.stringify(key_obj.key) + ' ' + CryptoJS.enc.Hex.stringify(key_obj.iv) + ' ' + CryptoJS.enc.Hex.stringify(key_obj.hash);
    
        var element = document.createElement('a');
        element.setAttribute('href','data:text/plain;charset=utf-8,' + file_content);
        element.setAttribute('download',filename + '.txt');
    
        element.style.display = 'none';
        document.body.appendChild(element);
    
        element.click();
        document.body.removeChild(element);
    }
});

