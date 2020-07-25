# Empathy API Definition

In the following, the UI - Backend Interface is described. On the one hand the game part uses socket protocol, the static content is transferred via REST service.

> Sequence diagrams are styled for js-sequence-diagrams https://bramp.github.io/js-sequence-diagrams/
> js-sequence is included in typora.

## Static information - REST API
The static content of the application like the game description is transferred via simple REST API. In the following all endpoints are defined.

### GET game general information

**Endpoint**
```
/games/{id}
```

**Sequence Diagram**
```sequence
UI->API (REST): /games/school-inclusion
Note right of Backend: Backend reads DB
API (REST)—>UI: { payload }
​```

**Payload**
```json
{
  Id: “school-inclusion”,
  Data: {
    Name: “School Inclusion”,
    Description: “...”,
    ...,
    Personas: [
      {
        Id: “teacher”,
        Name: “Teacher”,
        Description: “...”
      },
        Id: “parent”,
        Name: “Parent”,
        Description: “...”
      }
    ]
  }
}
``` 

### GET game persona information

**Endpoint**
```
/games/{id}/persona/{id}
```

**Sequence Diagram**
```sequence
UI->API (REST): /games/school-inclusion/personas/teacher
Note right of Backend: Backend reads DB
API (REST)—>UI: { payload }
​```

**Payload**
```json
{
  Id: “teacher”,
  Data: {
    Name: “Teacher”,
    Description: “...”,
    ...,
    Profile: [
      {
        Id: “empathy”,
        Name: “Empathic”,
        Description: “The ability to understand other peoples emotions”,
        Value: 9
      },
        Id: “philosophy”,
        Name: “Philosophy”,
        Description: “Am i conservative or progressive”,
        Value: 9
      }
    ]
  }
}
```


## Synchronous gaming - Socket.io
To achieve a synchronous information distribution within all players sockets are used. In the following all socket events are defined.


### Create new game

**Sequence Diagram**
```sequence
Note left of UI: Click on button “Create Game”
UI->API (socket):event: “connect”
Note right of API (socket): * sid (client connection id) is genereated\n* new user session is created
API (socket)->UI:101 - success/connected\nevent: “connect_successful”
UI->API (socket):event “new_game”\n{game_scenarion}
Note right of API (socket):* create new game and generate password for joining a game\n* assign user through sid/session to the game as host
API (socket)->UI:event “new_game”\n{game_id, game_pwd}
Note left of UI:Switch to view “Lobby”
``` 

### Join game
**Sequence Diagram**
```sequence
Note left of UI: Provide game ID and game password\nand click on button “Join game”\n
UI->API (socket):connect
Note right of API (socket):* sid (client connection id) is genereated\n* new user session is created
API (socket)—>UI: 101 - success/connected
UI->API (socket):event “join_game”\nwith “game_id” and “game_pwd”
Note right of API (socket):Check if game exists\nand password is correct. alt if game does not exist or password is wrong
Note over UI,API (socket): If not successful
API (socket)—>UI: event “invalid_game_or_pwd”
Note left of UI: Show error message
Note over UI,API (socket): If successful
Note right of API (socket):Add user to game as player. alt else
API (socket)—>UI:event “game_joined” with\nlist of players already waiting\nin the lobby.
Note left of UI: Switch to view “Lobby”
```




