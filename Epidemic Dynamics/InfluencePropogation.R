library(igraph)
#install.packages("akmeans")
library("akmeans")


influence_propagation <- function(graph, comm, beta=0.75){
  output = c()
  v = vcount(graph)
  nodes <- data.frame(1:v)
  colnames(nodes) <- c("Id")
  nodes$comm = comm
  nodes$color = "green"
  
  influencers = c()
  for(k in unique(comm)){
    influencer = sample(nodes[which(nodes$comm %in% k), c("Id")],1)
    influencers = append(influencers, influencer)           
  }
  
  nodes[nodes$Id %in% influencers, c("color")] <- "red"
  new_influencers = influencers
  total_influencers = length(influencers)
  
  timestep = 1
  old_influencers = 0
  ratio = total_influencers/v
  
  cat("Time Step = " , timestep,", Total Influencers = ", total_influencers, ", Network Coverage = " , ratio ,"\n")
  output = data.frame(timestep, total_influencers)
  
  timestep = timestep + 1
  alpha = 0.7
  
  #while(total_influencers - old_influencers > 0 && ratio < 1){
  for(i in 1:15){
    old_influencers = total_influencers
    influencers = new_influencers
    for(i in influencers){
      nbs = neighbors(graph, i)
      ## Selection if the propagation is inside community or outside
      flag = "inside"
      if(sample(1:100, 1) <= alpha*100){
        
        candidates = nodes[nodes$comm == nodes[i, c("comm")] & nodes$color == "green", c("Id")]
        candidates = intersect(candidates, nbs)
        ids <- c()
        for(j in candidates){
          if(j %in% nbs && sample(1:100, 1) <= beta * 100){     # Stochastically determining if node will get infected, using beta transmission probability
            ids <- append(ids, j)
          }  
        }    
      }else{
        candidates = nodes[nodes$comm != nodes[i, c("comm")] & nodes$color == "green", c("Id")]
        candidates = intersect(candidates, nbs)
        ids <- c()
        for(j in candidates){
          if(sample(1:100, 1) <= beta * 100){     # Stochastically determining if node will get infected, using beta transmission probability
            ids <- append(ids, j)
          }  
        }
      }
      nodes[which(nodes$Id %in% ids), c("color")] <- "red" 
      total_influencers = nrow(nodes[nodes$color == "red",])
      new_influencers = append(new_influencers, unique(ids))
    }  
    ratio = nrow(nodes[nodes$color == "red",])/v
    cat("Time Step = " ,timestep,", Total Influencers = ", total_influencers, ", Network Coverage = ", ratio ,"\n")
    output = rbind(output, data.frame(timestep, total_influencers))
    timestep = timestep + 1
  }
  output
}

