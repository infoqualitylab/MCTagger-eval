
#setup working directory
setwd("~/tagger_project")
list.files()

#Install RSQLite package, load DBI and read database 
install.packages("RSQLite");library(DBI)
# con<-dbConnect(RSQLite::SQLite(),
#                   dbname="all_predictions_1987_2016/all_predictions_1987_2016")
#--------upload newest database
con<-dbConnect(RSQLite::SQLite(),
               dbname="all_predictions_1987_2019/all_predictions_1987_2019")
#get .csv files from arrowsmith website and aggregate into single file for RCT tagger retrieval

# List all the tables available in the database
 dbListTables(con) #no explicit observational tables

#read query list of PubMed Ids; accession numbers only -- allow .ris files as input
ID<-read.csv("pubmed_id.csv", header=F)
ID.num<-as.numeric(unlist(ID))


#dump randomized controlled trial table from database
pred<-dbGetQuery(con, "SELECT * FROM RANDOMIZED_CONTROLLED_TRIAL")

#subset pred by ID
pred.rct<-pred[pred$id %in% ID.num,]

#results 1
r1<-data.frame(OriginalIDs=8911,Extracted_EndNote=nrow(ID), 
               Extracted_Predictions=nrow(pred.rct), MissingIDs=nrow(ID)-nrow(pred.rct))
r1
write.csv(r1,"results_table.csv")

#what are the missingIDs? -- compared iDs in pred.rct to ID
install.packages("BiocManager")
BiocManager::install("made4")
library(made4)
compare.ids<-comparelists(pred.rct$id, ID)
missing.ids<-compare.ids$Set.Diff

missing.ids<-ID.num[!ID.num %in% pred.rct$id]
db.missing<-data.frame(MissingIDs=missing.ids)
write.csv(db.missing, "missingIDs.csv" )

#culmulative line graph of data...
library(Hmisc)
install.packages('OneR')
library(OneR)
duration=pred.rct$prediction
range(duration)#0.0000000 0.9310345
breaks=seq(0,0.95,by=0.05)
duration.cut = cut(duration, breaks, right=FALSE)
duration.freq = table(duration.cut)
cumfreq0 = c(0, cumsum(duration.freq)) 
plot(breaks, cumfreq0,            # plot the data 
          main="Randomized Controlled Trials",  # main title 
          xlab="Tagger Prediction Probabilities",        # x???axis label 
          ylab="Cumulative RCT Articles")   # y???axis label 
lines(breaks,cumfreq0)
lines(rep(0.01,20),cumfreq0, col="red")     


pred.rct$threshold<-0.01
pred.rct$group<-duration.cut
write.csv(pred.rct, "rct_pred.csv")

library(stringr)
#missing pubmed ID years..
head(db.missing)
#get list of accession IDs and years/clean data
ID_year_raw<-read.csv('200123 OCR Library_acc_year.txt', header=F)
names(ID_year_raw)<-c("Year", "ID")
ID_year_raw$Year<-str_replace_all(ID_year_raw$Year, "[﻿]","")
ID_year_raw$ID<-str_replace_all(ID_year_raw$ID, "[.].*","")

#use function to get years from missing ids from accession list
year_missing<-ID_year[ID_year$ID %in% missing.ids,]
#what years are missing data from?
range(year_missing$Year)

#make a graph or table with y=proportions per x= year
# year_missing$count<-1
# year_missing<-year_missing[order(year_missing$Year),]
year_missing<-table(year_missing$Year)
year_missing<-as.data.frame(year_missing)
year_missing$per<-round(year_missing$Freq/sum(year_missing$Freq), digits=2)*100
#graph
library(ggplot2)
ggplot(year_missing,aes(x=Var1,y=per),fill=as.factor(Year))+
  geom_bar(position="dodge",stat="identity",color="blue")+
  geom_text(aes(label=paste0(per,"%")),position=position_dodge(width = 0.9),vjust=-0.25)+
  labs(x="Year of Study", y="% of articles missing")+
  theme_minimal()

write.csv(year_missing, "year_missing.csv")

#work savings - number of articles that can be disregarding at each prediction level
pred.freq<-data.frame(bin=c("0","0.0001","0.001","0.01","0.1",
                            "0.2","0.3","0.4","0.5","0.6","0.7",
                            "0.8","0.9","1"),perc_work=NA)

pred.freq[1,2]=length(which(pred.rct$prediction<0))/length(pred.rct$prediction)
pred.freq[2,2]=length(which(pred.rct$prediction<=0.0001))/length(pred.rct$prediction)
pred.freq[3,2]=length(which(pred.rct$prediction<=0.001))/length(pred.rct$prediction)
pred.freq[4,2]=length(which(pred.rct$prediction<=0.01))/length(pred.rct$prediction)
pred.freq[5,2]=length(which(pred.rct$prediction<=0.1))/length(pred.rct$prediction)
pred.freq[6,2]=length(which(pred.rct$prediction<=0.2))/length(pred.rct$prediction)
pred.freq[7,2]=length(which(pred.rct$prediction<=0.3))/length(pred.rct$prediction)
pred.freq[8,2]=length(which(pred.rct$prediction<=0.4))/length(pred.rct$prediction)
pred.freq[9,2]=length(which(pred.rct$prediction<=0.5))/length(pred.rct$prediction)
pred.freq[10,2]=length(which(pred.rct$prediction<=0.6))/length(pred.rct$prediction)
pred.freq[11,2]=length(which(pred.rct$prediction<=0.7))/length(pred.rct$prediction)
pred.freq[12,2]=length(which(pred.rct$prediction<=0.8))/length(pred.rct$prediction)
pred.freq[13,2]=length(which(pred.rct$prediction<=0.9))/length(pred.rct$prediction)
pred.freq[14,2]=length(which(pred.rct$prediction<=1))/length(pred.rct$prediction)

library(ggplot2)
ggplot(data=pred.freq, aes(x=bin, y=perc_work, group=1))+
  geom_line(color="red")+
  geom_point()+
  scale_color_grey()+theme_classic()+
  labs(x="RCT Predictor Thresholds", y="% work savings", 
      title="Percent of Articles Disregarded at RCT Predictor Thresholds")

#recall - actually articles included\full text versus what was captured from prediction?


save.image("pipeline.RData")
