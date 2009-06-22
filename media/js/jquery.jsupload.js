/*

JQuery.jsupload plugin. Allows to upload multiple files one-by-one.
Copyright (C) Elijah Merkin (http://evilyamantaka.livejournal.com)

This code is available under LGPL v3 license.

Requirements:

	jQuery
	jQuery.form

Usage:

	1. Include jquery.
	2. Include jquery.forms plugin.
	3. Include this file.
	4. Create an input with type="file".
	5. Insert the following script:

<script type="text/javascript"><!--
		$(function () {
			$('input[@type='checkbox']').jsupload ( here_go_the_options );
		});
--></script>

(You may replace "$('input[@type='checkbox']')" with any expression
that selects the desired DOM element)

	6. Arrange the server-side upload handling.


Options passed to jsupload should contain:

	name -- the name used by <INPUT> to post a file;
	upload_url -- the url to upload to;
	remove_img -- path to remove button image;
	upload_button_text (not required for English version) -- the text for upload button; 

*/

jsupload_uploaders = {};

function JSUploader ( options ) {
	this.options = options;
	this.element_str = '<input name="' + this.options.name + '" type="file" />';//</input>';
	this.id = this._generateId ();
	this.form_id = 'jsu_form_id_' + this.options.name + this.id;
	this.display_element = $("<table></table>"); 
	jsupload_uploaders[ this.form_id ] = this;
	var upload_text = "<a onclick='jsupload_uploaders[\"" + this.form_id + "\"].upload ();'>" +
		options.upload_button_text + "</a>";
	options.element.after(upload_text);
	this.animation = $("<img src ='" + options.animation + "' />");
	options.element.before(this.display_element);
	options.element.after (this.animation);
	this.animation.hide ();
	
	this.filelist = $ ("<input name='file_list_id_"+this.options.name+"' type='hidden' value='" +
		this.serializeVal(eval(this.options.value)) + "'></input>");
	this.display_element.before (this.filelist); //this.filelist.hide ();
	this.counter = 0;
	this.initDisplay (eval(this.options.value));

	var e = $(this.element_str);
	options.element.before (e);
	options.element.remove ();
	this.element = e;
}

JSUploader.prototype.current_id = 0;

JSUploader.prototype._generateId = function () {
	return JSUploader.prototype.current_id ++;
};

JSUploader.prototype.initDisplay = function (data) {
	this.display_element.empty ();
	for (var i = 0; i < data[0].length; i ++) {
		id = data[0][i];
		name = data[1][i];
		thumb = data[2][i];
		img = data[3][i];
		this.appendToDisplay (id, name, thumb, img);
	}
};

JSUploader.prototype.appendToDisplay = function (img_id, thumb_name, thumb_path, img_path) {
		file_id = 'f_' + this.form_id + this.counter; this.counter ++;
		remove_script = 'jsupload_uploaders[\'' + this.form_id +
		          '\'].removeFile (\'' + img_id + '\'); $(\'#' + file_id +'\').remove ();'
		thumb_code = '<a id="ltbox_' + file_id + '" href="' + img_path + '" class="lightbox" rel="' + 
					 this.form_id+'">' + '<img src="' + thumb_path + '" alt="' + thumb_name + '"/></a>';
		code = '<tr id = "' + file_id + '"><td>' + thumb_code + '</td><td>' +
		        thumb_name + '</td><td><img src="'+ this.options.remove_img +
		        '" onclick="' + remove_script + '"></img></td></tr>';
		this.display_element.append (code);
		var ref = $("#ltbox_" + file_id);
		if (ref ["lightbox"])
			ref.lightbox ();
};

JSUploader.prototype.upload = function () {
    this.form = $ ("<form id='" + this.form_id + "' method='POST' enctype='multipart/form-data'></form>" );
	this.element.remove ().appendTo (this.form);//.attr('name',this.options.name);
    this.form.appendTo ("body");
    var hook = function(obj, f) {
    	return function ( data ) {
    		f.call (obj, data);
    	};
    } (this, this.uploadOk);
    var error_hook = function(obj, f) {
    	return function (XMLHttpRequest, textStatus, errorThrown) {
    		f.call (obj, XMLHttpRequest, textStatus, errorThrown);
    	};
    } (this, this.uploadFailed);
    var call_data = {
    	url: this.options.upload_url,
    	dataType: 'text',
    	success: hook,
    	error: error_hook
    };
    this.animation.show ().next ().hide ();
    this.form.ajaxSubmit (call_data);
};

JSUploader.prototype.serializeVal = function (arr) {
	var p0 = '[[' + arr[0].toString () + '],[';
	var p1, p2, p3;
	if ( arr[1].length ) {
		p1 = '';
		for ( var i = 0; i < arr[1].length; i ++ ) {
			if ( i )
			  p1 += ',';
			p1 += '"';
			p1 += arr[1][i] + '"';
		}
		p1 += '],[';
	}
	else
		p1 = '],[';
	if ( arr[2].length ) {
		p2 = '';
		for ( var i = 0; i < arr[2].length; i ++ ) {
			if ( i )
			  p2 += ',';
			p2 += '"';
			p2 += arr[2][i] + '"';
		}
		p2 += '],[';
	}
	else
		p2 = '],[';
	if ( arr[3].length ) {
		p3 = '';
		for ( var i = 0; i < arr[3].length; i ++ ) {
			if ( i )
			  p3 += ',';
			p3 += '"';
			p3 += arr[3][i] + '"';
		}
		p3 += ']]';
	}
	else
		p3 = ']]';
	var v = p0 + p1 + p2 + p3;
	return v; 
};

JSUploader.prototype.uploadOk = function (data) {
	this.finalize ();
	var r = data.split ('|');
	if ( r[0] == 'image' ) {
		var img_id = r[1];
		var thumb_name = r[2];
		var thumb_path = r[3];
		var img_path = r[4];
		var arr = eval(this.filelist.val ());
		if (!arr)
			arr = [[],[],[],[]];
		arr[0].push(eval(img_id));
		arr[1].push(thumb_name);
		arr[2].push(thumb_path);
		arr[3].push(img_path);
		
		this.filelist.val (this.serializeVal (arr));
		this.appendToDisplay (img_id, thumb_name, thumb_path, img_path);

	};
};

JSUploader.prototype.uploadFailed = function (XMLHttpRequest, textStatus, errorThrown) {
    alert (errorThrown);
    this.finalize ();
};

JSUploader.prototype.removeFile = function (id) {
	var arr = eval(this.filelist.val ());
	id = eval(id)
	if (arr) {
		var idx = -1; var v = eval(id);
		for ( var i = 0; i < arr[0].length; i ++ )
			if (arr[0][i] == v) {
				idx = i;
				break;
			}
		if ( idx >= 0 ) {
			var v0 = arr[0].pop ();
			var v1 = arr[1].pop ();
			var v2 = arr[2].pop ();
			var v3 = arr[3].pop ();
			if ( idx != arr[0].length ) {
				arr[0][idx] = v0;
				arr[1][idx] = v1;
				arr[2][idx] = v2;
				arr[3][idx] = v3;
			}
			this.filelist.val(this.serializeVal(arr));
		}
	}
};

JSUploader.prototype.finalize = function () {

  this.animation.hide ().next ().show ();
  this.form.resetForm ();
  this.element.remove ();
  this.element = $(this.element_str);
  this.animation.before( this.element );
  this.form.remove ();
}; 


$.fn.jsupload = function ( options ) {
	options.element = this;
	ubtn = "Upload";
	if( "upload_button_text" in options )
		ubtn = options [ "upload_button_text" ];
	var uploader = new JSUploader ( options );
};
