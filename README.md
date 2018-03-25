# oauth2_proxy

Bitly [oauth2_proxy](https://github.com/bitly/oauth2_proxy) on eraldiseisev proxy server, mis implementeerib erinevate väliste teenusepakkujate (Google, Azure, Facebook, GitHub, GitLab, LinkedIn) kontode abil Oauth2 autentimise ja vahendab liiklust rakendusserverile lisades autentitud päringupäised.

### Arhitektuurilised alternatiivid
Oauth2_proxy liiklust võib seadistada erinevatel viisidel, süsteemiarhitektuurilise ülesehituse osas võib kasutada näiteks mõnda järgnevast võimalusest:

1. Kõik päringud käivad läbi oauth2_proxy. Konfiguratsiooni poolest lihtne, sobib rakendustele, millele peaksid ligi pääsema ainult sisse logitud kasutajad. Suurte mahtude korral võib proxy muutuda  märkimisväärselt ressursinõudlikuks. Ei ole soovitatav Oauth2_proxyt ilma sellele eelneva veebiserverita kasutada.
1. Backend server oauth2_proxy taga. Frontend ja staatiline sisu serveeritakse otse ja backend läbi Oauth2 proxy. Selle lahenduse puhul ei vaja proxy nii palju ressurssi, samal ajal kogu serveri poolel töötavale rakendusele ligipääs on proxy abil turvatud.
1. Sisse logimise meetod läbib oauth2_proxy, seal luuakse kasutajale näiteks lisaks oauth2_sessioonile  ka rakenduse sessioon või kasutatakse mõnd teist lähenemist. Ülejäänud rakendus töötab otse ja iseseisvalt. Selle lahenduse puhul peab arvestama, et oauth2_proxy serveerib ise html lehte, mis suunab sisse logimiseks väliste teenusepakkujate juurde ja sealt tagasi. Seega ei saa sisse logimist niisama lihtsalt taustal ajax päringuga teostada, vaid sisse logimise ajaks tuleb kontroll kogu veebisisu üle oauth2_proxy kätte usaldada.

### Nginx kasutamine oauth2_proxy koormusjaoturina (LBS).

Oauth2_proxy liikluse reguleerimiseks ja  jagamiseks on tavapärane kasutada Nginx veebiserverit. Nginx konfiguratsioon koosneb saitidest ja direktiivide plokkidest. Oauth2_proxy liikluse rakenduseni suunamiseks on võimalik kasutada kahte erinevat lähenemist:
 1. proxy_pass on harilik ja levinud nginx direktiiv, mis suunab antud ploki liikluse defineeritud proksisse koos defineeritavate parameetritega. Sealt edasi suunamine on defineeritud juba oauth2_proxy konfiguratsioonis ja võib toimuda otse või Nginx kaudu rakendussse. Järgnevas näites on oauth2_proxy defineeritud kuulama `localhost` pordil 4180. Näit:
 ```
    upstream oauth2_proxy {
     server 127.0.0.1:4180;
    }

    location / {
        proxy_pass http://oauth2_proxy;
        include proxy_params;
    }
```
 1. auth_request direktiivi kaudu, mis võimaldab Nginx-l autentida päringuid ilma kogu liiklust läbi proxy suunamata, vaid kasutades oauth2_proxy `/auth` sihtpunkti, mis vastab vastavalt accepted või unauthorized. Näit:
 ```
    location = /app/login {

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
        proxy_pass http://backoffice_app;
    }
```

### Praktiline näide

Alljärgnevat õpetust järgides saate Google Oauth2 kaudu oma rakendusse arenduskeskkonnas sisse logida.

* Mõelge välja mingi FQDN oma teenusele ja kirjutage see hosts faili ip aadressiks 127.0.0.1. Hosts faili kohta võite vastavalt oma platvormile lugeda näiteks [siit](https://en.wikipedia.org/wiki/Hosts_(file)). Siin näites kasutame serveriks nime local.example.com, kui seda muudate, siis tehke seda kõikjal.

* Pange püsti Nginx server. Tegemist on levinud veebiserveri tarkvaraga, mida siin projektis kasutame liikluse reguleerimiseks erinevate serverite vahel ja hea koht selle õppimisega alustamiseks võib olla näiteks [siin](https://www.nginx.com/resources/wiki/start/topics/tutorials/install/) Võtke käesolevast repost fail conf/etc/nginx/local.example.com.conf, muutke vajadusel seal seadistusi ja pange see nginx saitide konfiguratsioonide kataloogi.

* Minge [Google Developer konsooli](https://console.developers.google.com) ja looge oma (või oma firma) google konto alt uus projekt ja valigde Credentials alajaotus. Looge Oauth 2.0 client ID, application type on Web application, seadistage Authorized Redirect URI http://local.example.com/oauth2/callback , kirjutage üles client ID ja secret.
  Hätta jäädes saab lisainfot [Oauth2_proxy dokumentatsioonist](https://github.com/bitly/oauth2_proxy) ja  [Google dokumentatsioonist](https://developers.google.com/identity/protocols/OAuth2WebServer)

* Laadige alla oauth2_proxy viimane release oma platvormile [siit](https://github.com/bitly/oauth2_proxy/releases), muutke konfiguratsiooni parameetrid siin repos olevas conf/oauth2_proxy/oauth2_proxy.conf failis õigeteks. Käivitage oauth2_proxy inuxis näit. 
`./bin/oauth2_proxy -config conf/oauth2_proxy/oauth2_proxy.conf`

* Käivitage oma Spring Boot rakendus pordil 8080 või näidis Pythoni rakendus siit repost failist backend/main.py (backend kataloogis on selle käivitamine ka dokumenteeritud) Minge brauseriga http://local.example.com/ näete ilma oauth2_proxy-ta päringut ja oauth2_proxy-ga loginit. Kasutaja info pannakse päringu päisesse nii avatud kujul, kui ka kasutajanimi ka Basic Authorization päises.