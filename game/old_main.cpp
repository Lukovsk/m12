#include "WiFi.h"
#include "ESPAsyncWebServer.h"
// #include "Wire.h"
// #include "LiquidCrystal_I2C.h"
// LiquidCrystal_I2C lcd;
using namespace std;

const char *ssid = "Inteli-COLLEGE";
const char *password = "QazWsx@123";

// pinos
#define player1L 15 // LED vermelho (player 1)
#define player2L 11 // LED verde (player 2)
#define player3L 21 // LED amarelo (player 3)
#define player4L 2  // LED azul (player 4)
#define lightL 4    // LED branco (de controle do dia e noite)
// quero colocar um LCD pra mostrar o tempo também

// vetores auxiliares com os pinos dos LEDS e cores dos LEDS dos players
const int LEDS[5] = {player1L, player2L, player3L, player4L, lightL};
const String PColors[4] = {"red", "green", "yellow", "blue"};

int mortos[4];             // vetor com os players mortos
int fRN[4] = {1, 2, 3, 4}; // vetor com a ordem dos players
int period = 0;            // inteiro que mede o tempo (de 0 a 30 é dia e de 30 a 60 é noite)
bool witness = false;      // caso haja testemunha em um assassinato

AsyncWebServer web_server(80); // cria o objeto web_server

// funções
void restart() // reinicia todas as variáveis
{
    for (int i = 0; i < 4; i++)
    {
        mortos[i] = 0;
        fRN[i] = i + 1;
    }
    period = 0;
    witness = false;
    setup();
}

// função que fica piscando os leds
void piscapisca();

// função que retorna um botão padrão para o menu principal
String button(int paper, int number);

// função que retorna um botão padrão para as outras páginas que depende da porta
String button2(int port, int target, int player);

// função que retorna o "head" do html com o style e as meta tags
String head();

// função que retorna o html do menu
String menuHtml();

// funções que retornam o html do assassino, do detetive e da vítima respectivamente e leva o alvo de suas ações para as outras funções
String assassinHtml(int target);
String detectiveHtml(int target);
String victimHtml(int target, int port);

// funções que os players podem executar com seus papéis
void kill(int target);    // assassino - assassinar
void secure(int target);  // detetive - prender
void testify(int target); // vítima - testemunhar uma morte

// setup void
void setup()
{
    Serial.begin(9600); // inicia o serial

    // Wire.begin(47, 48); // 47-> LCA, 48 -> LCL
    // lcd.begin(16, 2);
    // lcd.setCursor(0, 0); // coluna, linha (linha de cima)
    // lcd.print("Tempo: ");
    // lcd.setCursor(0, 1); // linha de baixo
    // lcd.print(period);

    // define os pinos dos leds e ligá-os
    for (int i = 0; i < 5; i++)
    {
        pinMode(LEDS[i], OUTPUT);
        digitalWrite(LEDS[i], HIGH);
    }

    // tenta conectar ao wifi solicitado até conseguir
    Serial.println("Connecting to Wifi.. ");
    while (WiFi.status() != WL_CONNECTED)
    {
        WiFi.begin(ssid, password);
        delay(800);
        Serial.print(".");
        piscapisca();
    }

    // conectado à rede informada, ele printa o IP local
    Serial.println(WiFi.localIP());

    // randomiza os botões (infelizmente a randomização não funciona sempre, o padrão mantém: 1-Vitima, 2-Detetive, 3-Vitima, 4-Assassino)
    random_shuffle(fRN, fRN + 4);

    // página do menu
    web_server.on("/", HTTP_GET, [](AsyncWebServerRequest *req)
                  { req->send(200, "text/html; charset=UTF-8", menuHtml()); });

    // página do assassino
    web_server.on("/81", HTTP_GET, [](AsyncWebServerRequest *req)
                  { req->send(200, "text/html; charset=UTF-8", assassinHtml(-1)); });

    // página do detetive
    web_server.on("/82", HTTP_GET, [](AsyncWebServerRequest *req)
                  { req->send(200, "text/html; charset=UTF-8", detectiveHtml(-1)); });

    // páginas das vítimas
    web_server.on("/83", HTTP_GET, [](AsyncWebServerRequest *req)
                  { req->send(200, "text/html; charset=UTF-8", victimHtml(-1, 83)); });
    web_server.on("/84", HTTP_GET, [](AsyncWebServerRequest *req)
                  { req->send(200, "text/html; charset=UTF-8", victimHtml(-1, 84)); });

    // ações do assassino (pra matar outro player)
    web_server.on("/811", HTTP_GET, [](AsyncWebServerRequest *req)
                  { req->send(200, "text/html; charset=UTF-8", assassinHtml(0)); });
    web_server.on("/812", HTTP_GET, [](AsyncWebServerRequest *req)
                  { req->send(200, "text/html; charset=UTF-8", assassinHtml(1)); });
    web_server.on("/813", HTTP_GET, [](AsyncWebServerRequest *req)
                  { req->send(200, "text/html; charset=UTF-8", assassinHtml(2)); });
    web_server.on("/814", HTTP_GET, [](AsyncWebServerRequest *req)
                  { req->send(200, "text/html; charset=UTF-8", assassinHtml(3)); });

    // funções do detetive (para prender outro player)
    web_server.on("/821", HTTP_GET, [](AsyncWebServerRequest *req)
                  { req->send(200, "text/html; charset=UTF-8", detectiveHtml(0)); });
    web_server.on("/822", HTTP_GET, [](AsyncWebServerRequest *req)
                  { req->send(200, "text/html; charset=UTF-8", detectiveHtml(1)); });
    web_server.on("/823", HTTP_GET, [](AsyncWebServerRequest *req)
                  { req->send(200, "text/html; charset=UTF-8", detectiveHtml(2)); });
    web_server.on("/824", HTTP_GET, [](AsyncWebServerRequest *req)
                  { req->send(200, "text/html; charset=UTF-8", detectiveHtml(3)); });

    // funções da vítima 1 (para testemunhar um assassinato)
    web_server.on("/831", HTTP_GET, [](AsyncWebServerRequest *req)
                  { req->send(200, "text/html; charset=UTF-8", victimHtml(0, 83)); });
    web_server.on("/832", HTTP_GET, [](AsyncWebServerRequest *req)
                  { req->send(200, "text/html; charset=UTF-8", victimHtml(1, 83)); });
    web_server.on("/833", HTTP_GET, [](AsyncWebServerRequest *req)
                  { req->send(200, "text/html; charset=UTF-8", victimHtml(2, 83)); });
    web_server.on("/834", HTTP_GET, [](AsyncWebServerRequest *req)
                  { req->send(200, "text/html; charset=UTF-8", victimHtml(3, 83)); });
    // funções da vítima 2 (para testemunhar um assassinato)
    web_server.on("/841", HTTP_GET, [](AsyncWebServerRequest *req)
                  { req->send(200, "text/html; charset=UTF-8", victimHtml(0, 84)); });
    web_server.on("/842", HTTP_GET, [](AsyncWebServerRequest *req)
                  { req->send(200, "text/html; charset=UTF-8", victimHtml(1, 84)); });
    web_server.on("/843", HTTP_GET, [](AsyncWebServerRequest *req)
                  { req->send(200, "text/html; charset=UTF-8", victimHtml(2, 84)); });
    web_server.on("/844", HTTP_GET, [](AsyncWebServerRequest *req)
                  { req->send(200, "text/html; charset=UTF-8", victimHtml(3, 84)); });

    // inicia o servidor web
    web_server.begin();
}

// loop void
void loop()
{
    delay(200);
    period += 1;
    /*
    lcd.clear();
    lcd.setCursor(0, 0); // linha de cima
    if (period >= 30) {
         lcd.print("Está de noite");
    } else{
        lcd.print("Está de dia");
    }
    lcd.setCursor(0, 1); // linha de baixo
    lcd.print(String(period));
    */
    if ((period % 60) == 30) // se começa a ficar de noite
    {
        digitalWrite(LEDS[4], LOW);
        // se anoitecer com o assassino preso ou com a tentativa de assassinato do detetive, o detetive consegue se defender e ele e as vítimas ganham
        if ((digitalRead(LEDS[3]) == LOW) || (digitalRead(LEDS[1]) == LOW)) // player 4 or 2 (assassin or detective's death)
        {
            // detective and victims' win
            for (int i = 0; i < 10; i++)
            {
                piscapisca(); // festa
            }
            restart();
        }
    }
    if ((period % 60) == 0) // se estiver amanhecendo
    {
        digitalWrite(LEDS[4], HIGH);
        // se amanhecer com as vítimas mortas, o assassino ganha
        if ((digitalRead(LEDS[0]) == LOW) && (digitalRead(LEDS[2]) == LOW)) // player 1 and 3 (victim's death)
        {
            // assassin's win
            piscapisca();
            for (int i = 0; i < 3; i++)
            {
                digitalWrite(LEDS[i], LOW);
                delay(100);
            }
            delay(5000);
            restart();
        }
        // seta os leds consoante sua condição
        piscapisca();
        for (int i = 0; i < 4; i++)
        {
            if (mortos[i] == 1)
            {
                digitalWrite(LEDS[i], LOW);
            }
        }
    }
}

// retorna o botão que referencia a página padrão das portas das classes
String button(int paper, int number)
{
    String button = "<a class=\"btn\" href=\"8";
    button.concat(String(paper));
    button.concat("\" style=\"");
    button.concat(PColors[number]);
    button.concat("\"> Player ");
    button.concat(String(number + 1));
    button.concat("</a><br/>");
    return button;
}

// retorna o botão que referencia as ações das classes (por isso condiciona-se pela porta)
String button2(int port, int target, int player)
{
    String label = "";     // label do botão
    String condition = ""; // condição caso exista

    if (port == 81) // assassino
    {
        label = "Matar Player ";
        condition = " morto";
        kill(target); // apaga o led do alvo, basicamente
    }
    if (port == 82) // detetive
    {
        label = "Prender Player ";
        condition = " preso";
        secure(target); // apaga o led do alvo também
    }
    if ((port == 83) || (port == 84)) // vítimas
    {
        label = "Testemunhar Player ";
        condition = "";
        testify(target); // sabe quem é o assassino (printa que o assassino é o player 4 (amarelo))
    }
    // construção da tag <a></a>
    String button = "<a class=\"btn\" href=\"";
    button.concat(String(port));
    button.concat(String(player + 1));
    button.concat("\"><button class=\"btn\" style=\"background-color: ");
    button.concat(PColors[player]);
    if (player == 2)
    {
        button.concat("; color: black");
    }
    button.concat(";\">");
    button.concat(label);
    button.concat(String(player + 1));

    if (mortos[player] == 1)
    {
        button.concat(condition);
    }

    button.concat("</button>");
    button.concat("</a>");
    return button;
}

String head()
{
    String head = "";
    head.concat("<head>");
    head.concat("<meta name='viewport' content='width=device-width, initial-scale=1.0'>");

    head.concat("<style>");

    head.concat("body{ text-align: center; font-family: sans-serif; font-size: 14px; } ");

    head.concat("p{ color: #555; font-size: 12px; } ");

    head.concat("a{text-decoration: none;} ");

    head.concat(".btn{");
    head.concat("background-color: #2C5;");
    head.concat("color: #fff;");
    head.concat("outline: none;");
    head.concat("display: flex;");
    head.concat("align-items: center;");
    head.concat("justify-content: center;");
    head.concat("border: 1px solid #555;");
    head.concat("border-radius:18px;");
    head.concat("width: 150px;");
    head.concat("height: 30px;");
    head.concat("margin: 10px;");
    head.concat("margin-left: auto;");
    head.concat("margin-right: auto;");
    head.concat("cursor: pointer; } ");

    head.concat("h1 { text-align: center; } ");

    head.concat("</style>");
    head.concat("</head>");
    return head;
}

String menuHtml()
{
    String html = "";
    html = head();
    html.concat("<body>");
    html.concat("<h1> Jogo Detetive </h1><br/>");

    for (int i = 0; i < 4; i++)
    {
        html.concat(button(fRN[i], i));
    }

    html.concat("</body>");
    html.concat("</html>");
    return html;
}

String assassinHtml(int target)
{
    String html = "";
    html = head();
    html.concat("<body>");
    html.concat("<div>");
    html.concat("<h1> Você é o Assasino </h1> <div> <a href=\"/\"> Voltar </a> </div> <br/> </div>");

    for (int i = 0; i < 4; i++)
    {
        html.concat(button2(81, target, i));
    }

    html.concat("</body></html>");
    return html;
}

String detectiveHtml(int target)
{
    String html = "";
    html = head();
    html.concat("<body>");
    html.concat("<h1> Você é o Detetive </h1> <div> <a href=\"/\"> Voltar </a> </div> <br/> </div>");

    for (int i = 0; i < 4; i++)
    {
        html.concat(button2(82, target, i));
    }

    html.concat("</body></html>");

    return html;
}

String victimHtml(int target, int port)
{
    String html = "";
    html = head();
    html.concat("<body>");
    html.concat("<h1> Você é uma Vítima </h1> <div> <a href=\"/\"> Voltar </a> </div> <br/> </div>");

    // alguns botões?
    for (int i = 0; i < 4; i++)
    {
        html.concat(button2(port, target, i));
    }

    if (witness == true)
    {
        html.concat("<p>Você viu o assassinato! o assassino é o player 4 (azul)</p>");
    }

    html.concat("</body></html>");

    return html;
}

// ação que mata um alvo, o alvo PRECISA ser uma das vítimas, se não o assassino perde!
void kill(int target)
{
    if ((target == 1) || (target == 3)) // se o alvo for o player 2 ou 4 (detetive ou assassino), o assassino perde!
    {
        // assassin's lose
        mortos[3] = 1;
    }
    else
    {
        mortos[target] = 1; // caso contrário, é uma vítima, então ela morre
    }
}

// ação que prende um alvo, o alvo PRECISA ser o assassino, se não o detetive perde!
void secure(int target)
{
    if (target == 3) // se o alvo for o assassino, o detetive ganha
    {
        // detective's win
        mortos[3] = 1;
    }
    else
    {
        mortos[1] = 1; // caso contrário, é uma vítima ou ele mesmo, então o detetive perde!
    }
}

// ação que testemunha um alvo, o alvo pode ser qualquer um
// se o alvo for a outra vítima, você vê a morte dela e sabe quem é o assassino!
// se for o detetive acontece nada, nem se for o assassino (ele te engana)
void testify(int target)
{
    // o alvo é uma vítima e ela está morta

    if (((target == 0) || (target == 2)) && ((digitalRead(LEDS[0]) == LOW) || (digitalRead(LEDS[2]) == LOW)))
    {
        witness = true;
    }
}

// festa!
void piscapisca()
{
    for (int i = 0; i < 4; i++)
    {
        digitalWrite(LEDS[i], LOW);
        delay(50);
        digitalWrite(LEDS[i], HIGH);
    }
}