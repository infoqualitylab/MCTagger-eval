install.packages("RSQLite")
library(DBI)
library(stringr)
library(ggplot2)

#connect to database
db.1987.2019<-dbConnect(RSQLite::SQLite(), 
               dbname="~/Documents/Tagger Data/all_predictions_1987_2019")

#make variable for old taggers -- may take some time
RCT.taggers<-read.csv("~/Documents/Tagger Data/all.csv", sep="\t",header=T)

#read starting PubMed IDs
start.ids<-read.csv('OCR_RCT_START_IDS.txt', header=F)
names(start.ids)<-c("Year", "PubMed.ID")
start.ids<-str_replace_all(start.ids$PubMed.ID, "[.].*","")

#read retrieved abstracts 
abs.ret<-read.csv('OCR_RCT_RET_ABS_IDS.txt', header=F)
names(abs.ret)<-c("Year", "PubMed.ID")
abs.ret<-str_replace_all(abs.ret$PubMed.ID, "[.].*","")

