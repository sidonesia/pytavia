//----------------------------------------------------------//
//      The PyTAVIA SOCKET WRAPPER                          //
//              WRITTEN BY: Sid .B
//----------------------------------------------------------//

V_REQUEST_EVENT_INIT  = "PYTAVIA_REQUEST_EVENT_INIT";
V_RESPONSE_EVENT_INIT = "PYTAVIA_RESPONSE_EVENT_INIT";
V_CMD_EVENT           = "PYTAVIA_CMD_EVENT_INIT";

//
//      The EVENT MSG class that should have the
//              same format as that defined on the server
//
pytavia_event_msg = function(event_type , data)
{

    this.event_msg = {
        "event_type" : "",
        "event_time" : 0 ,
        "data"       : {}
    }

    this.put = function(event_type, data)
    {
        this.event_msg["event_type"] = event_type;
        this.event_msg["data"      ] = data;
    }

    this.get = function(key)
    {
        return this.event_msg[key];
    }

    this.json = function()
    {
        return this.event_msg;
    }

    this.stringify = function()
    {
        return JSON.stringify( this.event_msg );
    }
};

//
//      The EVENT PROCESSOR class that has the same event 
//              all the wrapper functions for making the pub sub
//              easy to use
//
pytavia_event_processor = function(socket_host, socket_port)
{
    var socket = io.connect('http://' + socket_host + ":" + socket_port);
    this.registered_handlers = new Array();

    //
    // Register the event and the callback
    //
    this.register = function(event_name, callback_func)
    {
        this.registered_handlers.push({
            "event_name"    : event_name,
            "callback_func" : callback_func
        })
    };

    //
    // Start the subscription
    //
    this.begin_subscribe = function()
    {
        socket.on( 
            'connect', 
            function() 
            {
                var p_event_msg = new pytavia_event_msg(
                    V_RESPONSE_EVENT_INIT, {}
                )
                socket.emit( 
                    V_REQUEST_EVENT_INIT, 
                    p_event_msg.json()
                )
            }
        )
        for (var idx = 0; idx < this.registered_handlers.length; idx++)
        {
            var subscribed    = this.registered_handlers[idx]
            var event_name    = subscribed.event_name;
            var callback_func = subscribed.callback_func;
            //
            // We register the callback functiosn based on the events
            //
            socket.on(  event_name,  callback_func  )
        }
    } 

    //
    // Publish changes to the server
    //
    this.publish = function( request )
    {
        var event_name = request.event_name;
        var event_data = request.event_data;

        var p_event_msg = new pytavia_event_msg(
            event_name, event_data
        );
        //
        // send the object back to the server based on 
        //      the event subscription type
        //
        socket.emit( event_name, p_event_msg.json() );
    }
    return this;
};

