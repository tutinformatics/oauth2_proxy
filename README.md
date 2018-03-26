# oauth2_proxy

[Bitly oauth2_proxy](https://github.com/bitly/oauth2_proxy) on eraldiseisev proxy server, mis implementeerib erinevate väliste teenusepakkujate (Google, Azure, Facebook, GitHub, GitLab, LinkedIn) kontode abil Oauth2 autentimise ja vahendab liiklust rakendusserverile lisades autenditud päringupäised.

### Süsteemiarhitektuur
Oauth2_proxy liiklust võib seadistada erinevatel viisidel, süsteemi ülesehituse osas võib kasutada näiteks mõnda järgnevast võimalusest:

1. Kõik päringud käivad läbi oauth2_proxy. Konfiguratsiooni poolest lihtne, sobib rakendustele, millele peaksid ligi pääsema ainult sisse logitud kasutajad. Suurte mahtude korral võib proxy muutuda  märkimisväärselt ressursinõudlikuks. Ei ole soovitatav Oauth2_proxyt ilma sellele eelneva veebiserverita kasutada.
1. Backend server oauth2_proxy taga. Frontend ja staatiline sisu serveeritakse otse ja backend läbi Oauth2 proxy. Selle lahenduse puhul ei vaja proxy nii palju ressurssi, samal ajal kogu serveri poolel töötavale rakendusele ligipääs on proxy abil turvatud.
1. Sisse logimise meetod läbib oauth2_proxy, seal luuakse kasutajale näiteks lisaks oauth2_sessioonile  ka rakenduse sessioon või kasutatakse mõnd teist lähenemist. Ülejäänud rakendus töötab otse ja iseseisvalt. Selle lahenduse puhul peab arvestama, et oauth2_proxy serveerib ise html lehte, mis suunab sisse logimiseks väliste teenusepakkujate juurde ja sealt tagasi. Seega ei saa sisse logimist niisama lihtsalt taustal ajax päringuga teostada, vaid sisse logimise ajaks tuleb kontroll kogu veebisisu üle oauth2_proxy kätte usaldada.

### Nginx kasutamine Oauth2_proxy eesmise _reverse proxy_-na  (LBS).

Veebiliikluse reguleerimiseks ja suunamiseks kasutatakse tihti Nginx veebiserveri tarkvara. Nginx konfiguratsioon on tavapäraselt jagatud erinevateks saitideks failidesse, mis koosnevad direktiivide plokkidest. Oauth2_proxy liikluse oma rakendusse suunamiseks Nginx abil on võimalik kasutada kahte erinevat lähenemist:
1. _proxy_pass_ on harilik ja levinud nginx direktiiv, mis suunab antud ploki liikluse defineeritud _proxy_sse koos defineeritavate parameetritega. Sealt edasi suunamine on defineeritud juba oauth2_proxy konfiguratsioonis ja võib toimuda otse või Nginx kaudu rakendussse. Järgnevas Nginx konfiguratsiooninäites on oauth2_proxy defineeritud kuulama `localhost` pordil 4180. Näit:
   ```
        upstream oauth2_proxy {
         server 127.0.0.1:4180;
        }
    
        location / {
            proxy_pass http://oauth2_proxy;
            include proxy_params;
        }
   ```
1. _auth_request_ direktiivi kaudu, mis võimaldab Nginx-l autentida päringuid ilma kogu liiklust läbi proxy suunamata, vaid kasutades oauth2_proxy `/auth` sihtpunkti, mis vastab vastavalt accepted või unauthorized. Näit:
   ```
    location = /login {

        # Auth request
        auth_request /oauth2/auth;
        error_page 401 = /oauth2/sign_in;
        auth_request_set $user   $upstream_http_x_auth_request_user;
        auth_request_set $email  $upstream_http_x_auth_request_email;
        auth_request_set $auth_cookie $upstream_http_set_cookie;
        add_header Set-Cookie $auth_cookie;

        # app
        include /etc/nginx/proxy_params;
        proxy_set_header App-User $user;
        proxy_set_header App-Email $email;
        proxy_pass http://backend;
    }
   ```

### Praktiline näide

Alljärgnevat õpetust järgides saate Google Oauth2 kaudu oma rakendusse arenduskeskkonnas sisse logida.

* Mõelge mingi FQDN oma teenusele ja määrake see hosts failis ip aadressiga 127.0.0.1. Hosts faili kohta võite vastavalt oma platvormile lugeda näiteks [siit](https://en.wikipedia.org/wiki/Hosts_(file)). Siin näites kasutame serveriks nime local.example.com, kui seda muudate, siis tehke seda kõikjal.

* Downloadige ja seadistage Nginx (/ɛndʒɪnɛks/ mitte  /ennkinks/) server. See on levinud veebiserveritarkvara, mida siin näites kasutame liikluse reguleerimiseks erinevate serverite vahel. Hea koht Nginx-iga esmatutvuse tegemiseks võib olla näiteks [siin](https://www.nginx.com/resources/wiki/start/topics/tutorials/install/) Downloadige [local.example.com.conf](https://github.com/tutinformatics/oauth2_proxy/blob/master/conf/etc/nginx/local.example.com.conf), muutke vajadusel seal seadistusi ja määrake see Nginx üheks saidiks.

* Logige sisse [Google Developer Console](https://console.developers.google.com),  looge uus projekt, valige Credentials alajaotus. Tekitage Oauth 2.0 client ID, kus _Application type_ on _Web application_. Seadistage _Authorized Redirect URI_-ks http://local.example.com/oauth2/callback , kirjutage üles client ID ja secret.
  Hätta jäädes saab lisainfot [Oauth2_proxy dokumentatsioonist](https://github.com/bitly/oauth2_proxy) või  [Google Oauth2 dokumentatsioonist](https://developers.google.com/identity/protocols/OAuth2WebServer)

* Laadige alla Bitly Oauth2_proxy viimane release oma platvormile [siit](https://github.com/bitly/oauth2_proxy/releases), muutke konfiguratsiooniparameetrid [oauth2_proxy.conf](https://github.com/tutinformatics/oauth2_proxy/blob/master/conf/oauth2_proxy/oauth2_proxy.conf) failis õigeteks. Käivitage oauth2_proxy koos oma konfiguratsioonifailiga. 
Linuxis näit: 
`./bin/oauth2_proxy -config conf/oauth2_proxy/oauth2_proxy.conf`

* Käivitage oma Spring Boot rakendus pordil 8080 või näidiseks toodud [Pythoni rakendus](https://github.com/tutinformatics/oauth2_proxy/tree/master/backend). Minge brauseriga http://local.example.com/ ja näete ilma oauth2_proxy-ta päringut ja oauth2_proxy-ga loginit. Kasutajainfo pannakse päringu päisesse nii avatud kujul, kui kasutajanimi ka _Basic Authorization_ päises.