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

return(sentiment)

}


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

