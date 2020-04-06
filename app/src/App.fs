module App

open Elmish
open Feliz

open Types

let init() =
    (), Cmd.none

let update (msg: Msg) (state: State) =
    (), Cmd.none

let render (state: State) (dispatch: Msg -> unit) =
    Html.h1 "Hello, world!"
