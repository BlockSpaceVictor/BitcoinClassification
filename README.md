# Simple Bitcoin Classification Repo

Here are some simple examples of bitcoin classfication and clustering, using k-means and (hopefully) other methods. The majority of the code is actually about creating a csv file that contains bitcoin address information. Information is gathered in the following way: 

1) Bitcoin full node is run 
2) I use Bitoin-etl to get node to download transaction history to .json file
3) I use MongoDB locally to read transactions into database 
4) From transaction outputs the program constructs a mongodb collection for addresses, excluding duplicates 
5) From previous transaction inputs and outputs, the "From-Addresses" are infrerred (Bitcoin does not directly store this information)
6) Various metrics are calculated from transaction information, such as first transaction timestamp, average transaction frequency, etc. These will be used as features in our machine learning model, or dimensions in clustering algorithm. The more the better
7) Read out address infomration to CSV file
8) Feed CSV file into any desired algorithm such as k-means clustering, etc. (k-means implemented here) 

## Todo:

- implement other clustering or classification algorithms 
- fix curser timeout issue of mongo (this prevents me from reading more than 30k transactions into the db at once)
- several of the mongo address functions can probably be more efficiently written or combined such as to reduce the number of complete database traversals 
- implement mongo indexes to increase speed
- implement multi-threading?
- alternatively, cut out mongo in the first place, work directly from json files, or use SQL database directly to feed into the clustering models 
- 

