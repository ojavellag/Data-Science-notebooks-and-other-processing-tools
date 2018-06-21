library(tidytext)
library(tidyverse)
library(glue)
library(stringr)
library(wordcloud)

files <- list.files("./R_stuff/Data/StateOfNation/")


# We start by reading the directory and by tokenizing the file
#using the next fuction

tokenizeFile <- function(sourceFile){

   fileName <- glue("./R_stuff/Data/StateOfNation/",
			  sourceFile,sep = "")
   fileName <- trimws(fileName)
   fileText <- readText <- glue(read_file(fileName))
   fileText <- gsub("//$","",fileText)

   tokens <-  data_frame(text = fileText)%>%unnest_tokens(word,text)
}

new100Words <- function(inFiles){

  myTokens <- NULL

  for(i in inFiles){
     myTokens <-rbind(myTokens,tokenizeFile(i))
  }
  wordsInBing <- get_sentiments("bing")[,1]

# Let's get the top 100 words in myTokens, which aren't stopWords nor
# are contained in the Bing lexicon

   top100Words <- myTokens %>%
    		      anti_join(stop_words)%>%
	            anti_join(wordsInBing)%>%
		      count(word, sort = T)%>%
		      top_n(100)

# saving the result to a csv file

   outName <- "100palabrasComunes.csv"
   targetFile <- glue("./R_stuff/Data/",outName,sep = "")

   write.csv(top100Words, targetFile) 
}



#the line below runs the two functions above (uncomment if needed)

#new100Words(files)



########################## 
# Here starts the exercise
########################## 

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

############################
#############################
# read the csv with the new words

file2Read <- "100palabrasComunes.csv"
file2Read <-trimws(file2Read)
InFile <- glue("./R_stuff/Data/",file2Read,sep = "")
newWords <- read.csv(InFile, header= TRUE,sep=",")
extndBing <- tibble(word=as.character(newWords[,2]),
			   sentiment=as.character(newWords[,3]))

extndBing <- extndBing %>% rbind(get_sentiments("bing"))

##############################
##############################


#Let's get the sentiment analysis, comparing the tokens against those of Bing Liu's study

sentiment <- tokens %>% 
inner_join(extndBing) %>%
count(sentiment) %>% # Number of positive/Negative words in Bing's study
spread(sentiment, n, fill=0) %>%

#get the number of sentiment words in a table
mutate(negative = negative/nrow(tokens))%>%
mutate(positive = positive/nrow(tokens))%>%
mutate(sentiment = positive-negative) %>%

mutate(file = file) %>%
mutate(year = as.numeric(str_match(file,"\\d{4}"))) %>%
mutate(president = str_match(file,"(.*?)_")[2])

return(sentiment)

}

########################
########################
#This part
#repeats the rest of the 
#tutorial
########################
sentiments <- data_frame()

for (i in files){
sentiments <-  rbind(sentiments,getSentiment(i))
}

## Let's now disambiguate the two cacorros bush, the cucho and the recucho 

bCucho <- sentiments %>%
filter(president == "Bush")%>%
filter(year < 2000) %>%
mutate(president = "bReCuchoCacorro")

bCacorron <- sentiments %>%
filter(president == "Bush")%>%
filter(year >= 2000) %>%
mutate(president = "PerroCacorro")

#This part removes the rows with the specific values filter in the given cols.
sentiments <- anti_join(sentiments, sentiments[sentiments$president == "Bush" & sentiments$year<2000, ])
sentiments <- anti_join(sentiments, sentiments[sentiments$president == "Bush" & sentiments$year>=2000, ])

sentiments <- full_join(sentiments,bCucho)
sentiments <- full_join(sentiments,bCacorron)

summary(sentiments)

#############################################################################
## Let's now visualize the results of our work

ggplot(sentiments,aes(x =as.numeric(year), y = sentiment)) + 
geom_point(aes(color = president))+
geom_smooth(method =  "auto")

#Notch plots

ggplot(sentiments, aes(x= president, y= sentiment, color = president))+
geom_boxplot()




#Final Part: How is the sentiment segregated by party

democrats<-sentiments %>%
filter(president == c("Clinton","Obama"))%>%
mutate(party = "D")

republicans<-sentiments %>%
filter(president != "Clinton" & president!="Obama")%>%
mutate(party = "R")

#joining the resulting table

byParty <- full_join(democrats,republicans)

t.test(democrats$sentiment,republicans$sentiment)

#ggplot(byParty, aes(x = party, y = sentiment, color = party))+
#geom_boxplot()+geom_point()




########################


