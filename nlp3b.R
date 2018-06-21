library(tidyverse)
library(tidytext)
library(glue)
library(stringr)


wd <- getwd()
files <- list.files("./R_stuff/Data/StateOfNation/")



#########################################
# creating a function with the same content
#but only passing the filename
#########################################

getSentiment <- function(file){

fileName<- glue("./R_stuff/Data/StateOfNation/",file,sep = "")

#removing spaces
fileName <- trimws(fileName)

#reading the preprocessed file
fileText <- glue(read_file(fileName))

#removing "$ sign"
fileText <- gsub("//$", "", fileText)

#Initial tokenization:
tokens <- data_frame(text= fileText) %>% unnest_tokens(word,text)


#Let's get the sentiment analysis, comparing the tokens against those of Bing Liu's study

sentiment <- tokens %>% 
inner_join(get_sentiments("bing")) %>%
count(sentiment) %>% # Number of positive/Negative words in Bing's study
spread(sentiment, n, fill=0) %>%

#get the number of sentiment words in a table
mutate(negative = negative/nrow(tokens))%>%
mutate(positive = positive/nrow(tokens))%>%
mutate(sentiment = positive-negative) %>%

mutate(file = file) %>%
mutate(year = as.numeric(str_match(file,"\\d{4}"))) %>%
mutate(president = str_match(file,"(.*?)_")[2])

return(tokens)

}

showWordCloud <- function(tokensFile){
  x11()
  myWords <- tokensFile%>%count(word) %>%
				      anti_join(stop_words)%>%
					with(wordcloud(word, n, max.words = 100))
}

listsOfWords <- data_frame()

ctr<-0
for (i in files){
   ctr<-ctr+1
   wordsInSpeech <-  rbind(listsOfWords,getSentiment(i))
   if(ctr==1 || ctr== 28 || ctr == 29){
   showWordCloud(wordsInSpeech)
   }

}









