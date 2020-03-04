#make working directory RCT CSV TAGGERS
setwd("~/tagger_project/MCTagger-eval/RCT CSV TAGGERS")

#create a variable which holds names of .csv files of RCT Taggers
file_list<-list.files()

#merge csv files into single dataframe
for (file in file_list){
  if (!exists("dataset")){
    dataset<-read.csv(file, header=T)
  }
  if (exists("dataset")){
    temp_dataset<-read.csv(file, header=T)
    dataset<-rbind(dataset, temp_dataset)
    rm(temp_dataset)
  }
}


