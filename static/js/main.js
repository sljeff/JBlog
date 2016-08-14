window.onload = function(){
  document.body.className = 'typo';
  var leftDiv = document.getElementById('firstDiv');
  var critileTop = leftDiv.offsetHeight - window.innerHeight;
  if(window.innerWidth > 600){
    if(critileTop <= 0){
      leftDiv.style.height = window.innerHeight+'px';
      leftDiv.style.position = 'fixed';
    }else{
      document.addEventListener('scroll', function(e){
        if(window.scrollY >= critileTop){
          leftDiv.style.top = -critileTop+'px';
          leftDiv.style.position = 'fixed';
        }else{
          leftDiv.style.top = 0;
          leftDiv.style.position = 'absolute';
        }
      });
    }
  }else{
    window.scrollTo(0, leftDiv.clientHeight-50);
  }
}