#ifndef GHOST_LIB_METIRCS_H_
#define GHOST_LIB_METIRCS_H_

#include <cstdint>
#include <iostream>
#include <vector>
#include <fstream>
#include <sstream>
#include <unordered_map>
#include <filesystem>

using namespace std;
unordered_map<string,int> all_metrics;
unordered_map<int,unordered_map<string,int>> pid_metrics;
unordered_map<int,unordered_map<string,unordered_map<string,int>>> pid_task_metrics;


vector<string> split (const string &s, char delim) {
    vector<string> result;
    stringstream ss (s);
    string item;

    while (getline(ss, item, delim)) {
        result.push_back (item);
    }

    return result;
}

unordered_map<string,int> spec_read(){
    std::ifstream infile("specFile.spec");
    unordered_map<string,int> specs;
    if (infile.is_open()){
        string tp;
         while(getline(infile, tp)){
            vector<string> tokens=split(tp,',');
            specs[tokens[0]]=std::stoi(tokens[1]);
         }
         infile.close();
   }
   return specs;
}

unordered_map<string,int> spec_read(string specfilename){
    std::ifstream infile(specfilename);
    int lineNo=0;
    unordered_map<string,int> specs;
    if (infile.is_open()){
        string tp;
         while(getline(infile, tp)){
            if(lineNo==0){     
                lineNo++;
                continue;
            }
            vector<string> tokens=split(tp,',');
            specs[tokens[0]]=std::stoi(tokens[1]);
         }
         infile.close();
   }
    else{
        printf("File not found!");
    }
   return specs;
}

void all_metrics_read(string metrics){
    std::ifstream infile(metrics);
    int lineNo=0;
    if (infile.is_open()){
        string tp;
         while(getline(infile, tp)){
            if(lineNo==0){     
                lineNo++;
                continue;
            }
            vector<string> tokens=split(tp,',');
            if(tokens[0]=="ALL"){
                all_metrics[tokens[1]]=std::stoi(tokens[2]);
            } 
            if(tokens[0]=="PID"){
                int pid=std::stoi(tokens[1]);
                if (pid_metrics.find(pid) != pid_metrics.end()){
                    unordered_map<string,int> syscall_count_by_pid;
                    pid_metrics[pid]=syscall_count_by_pid;
                }
                 pid_metrics[pid][tokens[2]]=std::stoi(tokens[3]);
            }
         }
         infile.close();
   }
}

void print_metrics(){
    unordered_map<string,int> specs=spec_read("/home/ocollaco/ghost-specialized-ps-userspace/schedulers/cfs/specFile.spec");
    for (auto& it: specs) {
        cout << it.first.c_str()<<it.second;
        printf("%s : %d", it.first.c_str(), it.second);
    }

    all_metrics_read("/home/ocollaco/ghost-specialized-ps-userspace/schedulers/cfs/metrics.csv");
    for (auto& it: specs) {
        //cout << it.first.c_str()<<it.second<<endl;
        printf("%s : %d", it.first.c_str(), it.second);
    }
    for(auto& it:all_metrics){
        //cout<<it.first.c_str()<<" value "<<it.second<<endl;
        printf("%s value: %d", it.first.c_str(), it.second);
    }

    for(auto& it:pid_metrics){
        unordered_map<string,int> pid_metric_val=it.second;
        for(auto& it2:pid_metric_val){
                    //cout<<"PID:"<<it.first.c_str()<<" : "<<it2.first<<" :"<<it2.second<<endl;
                printf("PID %d : %s : %d", it.first, it2.first.c_str(), it2.second);

        }
    }
}

#endif