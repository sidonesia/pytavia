var event_processor = null;
var last_api_call   = new Date().getTime();
var five_seconds    = 1 * 600;
var current_id      = Math.floor(Math.random() * (9999999 - 1000000 + 1) + 1000000);

var prev_x = null;
var prev_y = null

$( document ).ready(
    function()
    {
        //
        // create the event handler processor to accept
        //      and connect on port 5000
        //
        var pep = new pytavia_event_processor(
            document.domain, "5000"
        );

        //
        // register the event we want to listen on and the
        //      callback handler here
        //
        pep.register(
            "PYTAVIA_CMD_EVENT_INIT", callback_draw_data
        );

        //
        // start our subscription process
        //
        pep.begin_subscribe();

        //
        // send a HI to the server to make sure we are connected
        //      and for the counter
        //
        pep.publish ({
            event_name : "PYTAVIA_REQUEST_EVENT_INIT",
            event_data : {
                "msg"  : "Hi .. ack",
                "time" : new Date().getTime(),
                "port" : 5000
            }
        })
    }
);

callback_draw_data = function( msg )
{
	var sender_id = msg.data.current_id;
	var canvas    = document.getElementById('imageView');
    	var context   = canvas.getContext('2d');
	if ( parseInt(sender_id) == current_id )
	{
		return;
	}

	var type = msg.data.type;
	var ev_x = msg.data.ev_x;
	var ev_y = msg.data.ev_y;

	if ( type == "move-to" )
	{
		context.beginPath();
		context.moveTo(ev_x, ev_y);
		return;
	}

	console.log ( "from server: " + ev_x + " " + ev_y + " " + sender_id + " " + current_id );

    	if (!context) 
	{
      		alert('Error: failed to getContext!');
      		return;
    	}
       	context.lineTo(ev_x, ev_y);
        context.stroke();
};

// Keep everything in anonymous function, called on window load.
if(window.addEventListener) {
window.addEventListener('load', function () {
  var canvas, context, tool;

  function init () {
    // Find the canvas element.
    canvas = document.getElementById('imageView');
    if (!canvas) {
      alert('Error: I cannot find the canvas element!');
      return;
    }

    if (!canvas.getContext) {
      alert('Error: no canvas.getContext!');
      return;
    }

    // Get the 2D canvas context.
    context = canvas.getContext('2d');
    if (!context) {
      alert('Error: failed to getContext!');
      return;
    }

    // Pencil tool instance.
    tool = new tool_pencil();

    // Attach the mousedown, mousemove and mouseup event listeners.
    canvas.addEventListener('mousedown', ev_canvas, false);
    canvas.addEventListener('mousemove', ev_canvas, false);
    canvas.addEventListener('mouseup',   ev_canvas, false);
  }
  //
  // This painting tool works like a drawing pencil which tracks the mouse 
  // movements.
  //
  function tool_pencil () {
    var tool = this;
    this.started = false;

    // This is called when you start holding down the mouse button.
    // This starts the pencil drawing.
    // 
    this.mousedown = function (ev) {
        context.beginPath();
        context.moveTo(ev._x, ev._y);
        tool.started = true;
        AJAX_SERVER_call(
            callback_display_transaction_value,
            "GET",
            "/api/process/move-to-write",
            {
                    ev_x        : ev._x ,
                    ev_y        : ev._y ,
                    current_id  : current_id
            },
            true
        );
    };
    //
    // This function is called every time you move the mouse. Obviously, it only 
    // draws if the tool.started state is set to true (when you are holding down 
    // the mouse button.
    // 
    this.mousemove = function (ev) {
      if (tool.started) {
        context.lineTo(ev._x, ev._y);
        context.stroke();
	//
	// send the ajax server call 
	//
        AJAX_SERVER_call(
            callback_display_transaction_value,
            "GET",
            "/api/process/write",
            { 
		    ev_x 	: ev._x , 
		    ev_y 	: ev._y , 
		    current_id 	: current_id 
	    },
            true
        );
      }
    };

    // This is called when you release the mouse button.
    this.mouseup = function (ev) {
      if (tool.started) {
        tool.mousemove(ev);
        tool.started = false;
      }
    };
  }

  // The general-purpose event handler. This function just determines the mouse 
  // position relative to the canvas element.
  function ev_canvas (ev) {
    if (ev.layerX || ev.layerX == 0) { // Firefox
      ev._x = ev.layerX;
      ev._y = ev.layerY;
    } else if (ev.offsetX || ev.offsetX == 0) { // Opera
      ev._x = ev.offsetX;
      ev._y = ev.offsetY;
    }

    // Call the event handler of the tool.
    var func = tool[ev.type];
    if (func) {
      func(ev);
    }
  }

  init();

}, false); }

callback_display_transaction_value = function( msg_json )
{

}

AJAX_SERVER_call = function(callback_func, method, wservice, uri, bool)
{
        var jqxhr = $.ajax(
        {
                url      : wservice ,
                method   : method   ,
                data     : uri      ,
                dataType : "json"
        }).done(
                function(msg_json)
                {
                        callback_func(msg_json);
                }
        ).fail(
                function(msg_json)
                {
                        callback_func(msg_json);
                }
        ).always(
                function()
                {
                }
        );
};

