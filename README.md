# Rascolitorul Web

## Scopul apicatiei

- Poti cauta cele mai comune/frecvent intalnite informatii despre un anumit subiect.
- Poate bagam si un ranking genul:

        Pentru cautarea "pisici"
        - 80% din surse afirma ca pisicile sunt animale de companie
        - 19% din surse afirma ca pisicile sunt animale salbatice
        - 1% din surse afirma ca pisicile sunt bacterii

## Tech Stack-ul folosit

- Frontendul este scris in Typescript + React + ReactBootstrap pentru styling (Asi vrea sa folosim stylingul de la bootsrap sa mai invat si io)
- 1 Web service de backend va fi in python + Flask
- 1 Web service de backend va fi in C# + ASP.NET

Voi explica flowul aplicatiei:

1. Userul scrie in search bar subiectul dorit
2. Textul introdus de user e trimis catre web service-ul in python unde vom face crawling pe site-uri si luam informatii (Aicea nu stiu exact de pe ce site-uri yet)
3. In web service-ul din python se va creea un fisier pt. fiecare site crawluit cu informatiile gasite de pe site in format string.(Doar scrii stringu/stringurile in fisier). Ex: vom avea **pisici.org.txt** si **wikipedia.txt** ,iar fiecare fisier va avea tag-ul **cats**. Dupa, va face un call catre web service-ul din C# catre functia **upload** si dupa catre **ask**.

In web serviceul din C# vom defini 2 endpoint-uri importante:

**upload** (care va primi ca argument un fisier/fisiere din care AI-ul dupa o sa poata sa ia informatii)

**ask** (care va primi ca argument un string cu o intrebare pt. AI si niste tag-uri dupa care vom filtra prin ce fisiere o sa caute). Intrebarea o sa fie de genul: "What was the most common fact about cats among the files given to you." si tagurile dupa care filtram fisiere o sa fie "cats".

Doar in C# avem libraria cu AI pe care stiu ca o putem folosi, de aia avem 2 servere de backend.

4. Dupa ce web serviceul din python primeste rezultatul de la endpointu ask, o sa fie transmis inapoi catre frontend unde va fi afisat.

## Chestii de instalat

- VSCode (recomandat, de 10 ori mai bun ca sublime, in special pt React)
- VStudio daca vrei sa faci la aia cu C#
- https://github.com/microsoft/kernel-memory asta e musai sa rulezi, e libraria din C# care ne lasa sa folosim AI sa cautam in fisiere
- https://ollama.com/ de aici vom instala local 2 modele care o sa fie folosite de libraria din C# **llama2:7b** si **mxbai-embed-large:latest**

## Pt. instalat kernel-memory

- Fork la repo
- In directoriu kernel-memory/ai_web_service/ai_web_service.csproj ai chestia asta **Include="C:\Faculta\Licenta\TESTAM\kernel-memory\extensions\KM\KernelMemory\KernelMemory.csproj"**
- Schimbi pathul asta la fisierul unde ai instalat libraria de pe git

## Pt. instalat modelele

- pornesti ollama
- deschizi un terminal si scrii
  - ollama pull llama2:7b
  - ollama pull mxbai-embed-large:latest
- tocmai te-am facut sa-ti descarci mai mult de 4GB
- ollama trebe sa ruleze atunci cand merge web service-ul in C#. Nu trebuie modelele pornite, doar ollama trebuie sa ruleze in fundal
