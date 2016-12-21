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

 // var maxScroll = document.getElementById('lastDiv').offsetHeight - window.innerHeight;
 // var addComment = function(){
 //   if(maxScroll-window.scrollY<300){
 //       document.getElementById('lAdd1').innerHTML = '<div id="disqus_thread"></div>'
 //       var disqus_config = function () {
 //       this.page.url = window.location.href; // Replace PAGE_URL with your page's canonical URL variable
 //       this.page.identifier = window.location.pathname.split('/')[2]; // Replace PAGE_IDENTIFIER with your page's unique identifier variable
 //       };
 //       (function() { // DON'T EDIT BELOW THIS LINE
 //       var d = document, s = d.createElement('script');
 //       s.src = '//shan-liang-de-jie-fu.disqus.com/embed.js';
 //       s.setAttribute('data-timestamp', +new Date());
 //       (d.head || d.body).appendChild(s);
 //       })();
 //       document.removeEventListener('scroll', addComment, false);
 //   }
 // }
 // if(window.location.pathname.split('/')[1]=='a'){
 //   document.addEventListener('scroll', addComment);
 // }

  var fAdd1 = document.getElementById('fAdd1');

  about = document.createElement('div');
  about.classList = 'list';

  github = document.createElement('a');
  github.href = 'https://github.com/sljeff/';
  github.innerHTML = 'Github';

  email = document.createElement('a');
  email.href = 'mailto:kindjeff.com@gmail.com';
  email.innerHTML = 'kindjeff.com@gmail.com';

  about.appendChild(email);
  about.appendChild(github);
  fAdd1.appendChild(about);
}
