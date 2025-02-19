## Scopul apicatiei

- Poti cauta cele mai comune/frecvent intalnite informatii despre un anumit subiect.
## Tech Stack-ul folosit

- Frontendul este scris in Typescript + React + ReactBootstrap pentru styling
- 1 Web service de backend in python + Flask
- 1 Web service de backend in C# + ASP.NET
  
## Pt. instalat modelele
- pornesti ollama
- deschizi un terminal si scrii
  - ollama pull llama3.2:latest
  - ollama pull nomic-embed-text:latest
  - ollama trebe sa ruleze atunci cand merge web service-ul in C#. Nu trebuie modelele pornite, doar ollama trebuie sa ruleze in fundal.

 ### Rulare
 - Fork la repo
 - Din radacina proiectului.
 1. Pentru web service-ul in C#
    - cd ai_web_service/
    - ollama serve
    - dotnet run
 2. Pentru web service-ul in python
    - cd backend/
    - flask --app main.py run
 3. Pentru frontend
    - cd frontend/
    - npm run dev 
