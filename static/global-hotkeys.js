/*
Usage example:

   <a data-hotkey="f" href="/foobar">FooBar</a>

*/
function setup_global_hotkeys()
 {
     var hotkeys = Array();

     $("a[data-hotkey]").each(function(idx,x){
         var e = $(x);
         const hotkey = e.data("hotkey").toLowerCase().charCodeAt(0);
         hotkeys[hotkey] = x;
     });
     $(document).keypress(function(event){
         if (event.which in hotkeys) {
             var x = hotkeys[event.which] ;
             //console.log("Simulating click on ", x);
             $(x)[0].click();
         }
     });
     //console.log(hotkeys);
 }

 $(function(){
     setup_global_hotkeys();
 });
