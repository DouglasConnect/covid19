module App

open Elmish
open Feliz
open Feliz.Bulma
open Types

let init() = (), Cmd.none

let update (msg: Msg) (state: State) = (), Cmd.none

let render (state: State) (dispatch: Msg -> unit) =
    Html.div
        [ Bulma.hero
            [ prop.children
                [ Bulma.heroBody
                    [ Bulma.container
                        [ prop.children
                            [ Bulma.title [ Html.h1 "Covid-19 data in Edelweiss Data" ]
                              Bulma.subtitle
                                  [ Html.h2
                                      "Properly versioned, daily updated COVID-19 data from multiple sources exported as JSON, consumable via a Python library and displayed in a rich UI" ]
                              Html.a
                                [ prop.href "https://ui.develop.edelweiss.douglasconnect.com/datasets?q=%7B%22filters%22%3A%7B%22Dataset%20category%22%3A%5B%22covid-19%22%5D%7D%7D"
                                  prop.children
                                    [ Html.img
                                          [ prop.style [ style.width (length.percent 50) ]
                                            prop.src "images/dataexplorer.png" ] ] ] ] ] ] ]
                                ]

          Bulma.section
              [ prop.children
                  [ Bulma.container
                      [ prop.children
                          [ Html.p
                              "Edelweiss Data is a data management platform we built for managing scientific data of EU research projects. For our exploratory Covid-19 projects we used EdelweissData to help us with republishing and aggregating data from various sources in different formats. It allows us to deliver daily updates while always preserving previous versions for full reproducibility. All data is served as JSON which can be consumed easily by web applications that visualize it and create predictions. Complementing the REST API, our rich UIs enable users to dive into the underlying data to check and verify every data point."
                            Html.p
                                [ prop.text
                                    "The following data sources are available for non-commercial purposes in the form of REST APIs to the public:"
                                  prop.children
                                      [ Html.ul
                                          [ prop.children
                                              [ Html.li
                                                  [ Html.a
                                                      [ prop.href
                                                          "https://ui.develop.edelweiss.douglasconnect.com/dataexplorer?dataset=e06e9223-5e5d-42c2-a090-feba0bcee19a%3A16"
                                                        prop.text "COVID-19 dataset by Our World In Data" ] ]
                                                Html.li
                                                    [ Html.a
                                                        [ prop.href
                                                            "https://ui.develop.edelweiss.douglasconnect.com/dataexplorer?dataset=ea0f33fd-d47b-445d-bbe8-92d62cec4e06%3A13"
                                                          prop.text "COVID-19 dataset by John Hopkins University" ] ]
                                                Html.li
                                                    [ Html.a
                                                        [ prop.href
                                                            "https://ui.develop.edelweiss.douglasconnect.com/dataexplorer?dataset=0844d662-a6fa-4c1a-8fc4-2862cb33294b%3A3"
                                                          prop.text
                                                              "COVID-19 state level data by the Robert Koch Institute" ] ]
                                                Html.li
                                                    [ Html.a
                                                        [ prop.href
                                                            "https://ui.develop.edelweiss.douglasconnect.com/dataexplorer?dataset=6fb456f4-da54-4a23-ab89-8410ddec3851%3A5"
                                                          prop.text "COVID-19 US state level data by the New York Times" ] ] ] ] ] ] ] ] ] ]
          Bulma.section
              [ prop.children
                  [ Bulma.container
                      [ prop.children
                          [ Bulma.title2 "Examples"
                            Bulma.columns
                                [ Bulma.column
                                    [ Bulma.column.isOneQuarter
                                      prop.children
                                          [ Html.a
                                              [ prop.href "https://covid-19.sledilnik.org/"
                                                prop.children [ Html.img [ prop.src "images/example-slovenia.png" ] ] ] ] ]
                                  Bulma.column
                                      [ Bulma.title3 "Slovenian case data dashboard"
                                        Html.p
                                            """Data for Slovenia was poorly presented in the early days of the SARS-COV-2 outbreak so we helped a team of volunteers to
                                               create a rich visualisation of the daily development of cases, deaths and hospitalisation counts. Pulling data into a web application as
                                               json made it easy to develop visualisations quickly.""" ] ]
                            Bulma.columns
                                [ Bulma.column
                                    [ Bulma.column.isOneQuarter
                                      prop.children
                                          [ Html.a
                                              [ prop.href
                                                  "https://observablehq.com/@danyx/estimating-sars-cov-2-infections"
                                                prop.children [ Html.img [ prop.src "images/example-notebook.png" ] ] ] ] ]
                                  Bulma.column
                                      [ Bulma.title3 "Estimating true infections from COVID-19 deaths"
                                        Html.p
                                            """In this notebook we explored the idea of estimating the number of truly infected individuals in a population from confirmed
                                               COVID-19 deaths. Assuming that COVID-19 deaths should be discovered with a higher probability than (possibly asymptomatic or mild)
                                               cases, the notebook interactively estimates the number of truly infected."""
                                        Html.p
                                            """The data is updated daily from several important data sources using Github Actions that run Python scripts using pandas for data
                                               restructuring and our EdelweissData python client for easy uploading of new versions. By treating every version as an immutable dataset
                                               it is always possible to go back in time and check predictions based on past data. The rich metadata support of Edelweiss Data came in
                                               handy to communicate things like the origin of every dataset, the date and time of data retrieval and links to more in-depth information.""" ] ] ] ] ] ]
          Bulma.section
              [ prop.children
                  [ Bulma.container
                      [ prop.children
                          [ Bulma.title2 "Details of the workflow"
                            Html.p
                                """We are always interested in adding additional datasets that might be useful for the public. What follows is a description of the process of preparing, publishing
                                   and consuming data via Edelweiss Data and a description of what you can do to add a dataset."""
                            Bulma.title4 "Ingesting the data"
                            Html.p
                                """It all starts with the URL of the data you want to publish into Edelweiss data. Very often this will be a CSV file that is updated every day, but for some publishers
                                   it may also be just an html table with case numbers etc or an Excel file. """
                            Html.p
                                """We want to automate the retrieval and publishing of the data so it can be done automatically in regular intervals via Github Actions. Github Actions is a service
                                   provided by Github that is often used to compile software artifacts, but it can just as well be used to prepare data. Github actions can run a wide variety of scripting
                                   languages and what is not supported directly can be run inside docker containers.  """
                            Html.p
                                """In our examples (LINK) we used Python with the popular Pandas library to download the original datasets and in some cases reformat the data (e.g. to go from a dataset
                                   that has cases in countries as rows and days as columns to a long form dataset where every row is one observation of cases for one date and one country). When developing
                                   these scripts we often work in Jupyter notebooks to iteratively check if the reshaping of the data works the way it is intended to work."""
                            Html.p
                                """When we are happy with reshaping the data (or the data was already formatted well), the next step is to upload the data. For this we use our EdelweissData python library
                                   (LINK) to upload the data together with a metadata in json form that describes the retrieval data and the upstream data provider as well as a description text that tells
                                   human consumers more about this dataset. The first time this is done a new dataset has to be created. For subsequent steps, instead of creating a new dataset we want to
                                   find an already published dataset (either by ID or by other criteria), and then publish a new version of this dataset - the code is almost identical in both cases."""
                            Html.p
                                """Once the dataset is published for the first time you can see the result in the EdelweissData UI."""
                            Bulma.title4 "Automatically updating data"
                            Html.p
                                """To trigger automatic publishing of updates, we then set up the Github Action itself. This is a yaml file (LINK) that describes which actions to execute and how this is
                                   triggered (in our case a cron trigger that executes once a day at a specified time). The results of these actions can be seen in the Actions panel of the github
                                   repository page, but of course the scripts themselves can also notify their authors via email, slack or other means about the status of the import process."""
                            Bulma.title4 "Viewing and consuming data"
                            Html.p
                                """The first thing you will probably want to do after publishing a dataset is to check if the data does indeed look the way you think it should. For this, browse to the
                                   EdelweissData UI (LINK) and click on your dataset to see its data in the DataExplorer. The interface is tabbed and next to the data tab you can also find the description
                                   (human readable text explaining the dataset) and the metadata (json encoded machine readable metadata). """
                            Html.img [prop.src "images/dataexplorer-top.png"]
                            Html.p
                                """In the data tab you can filter data by entering search terms in the dataset search box or in one of the individual columns search box. On the top right you can find a
                                   button titled “API” that shows the code to download the data as currently filtered either via the Python library or via a curl command. The download button allows
                                   downloading a CSV of the currently filtered selection."""

                                   ] ] ] ] ]
