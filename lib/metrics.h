#ifndef GHOST_LIB_METIRCS_H_
#define GHOST_LIB_METIRCS_H_

#include <cstdint>
#include <iostream>
#include <vector>
#include <fstream>
#include <sstream>
#include <unordered_map>
#include <filesystem>
#include<unordered_set>


namespace ghost{
class Metrics{
    private:
    std::unordered_map<std::string,int> specs;
    std::unordered_map<std::string,int> all_metrics;
    std::unordered_map<int,std::unordered_map<std::string,int>> pid_metrics;
    // std::unordered_map<int,std::unordered_map<std::string,std::unordered_map<std::string,int>>> pid_task_metrics;
    std::unordered_map<int,bool> allow_preemption;
    std::unordered_set<int> unique_pids;

    std::unordered_map<int,int64_t> pid_metric_staleness;
    bool general_preemption=true;
    std::vector<std::string> syscalls;
    //std::filesystem fs;
    std::string current_path;



    std::vector<std::string> split (const std::string &s, char delim) {
            std::vector<std::string> result;
            std::stringstream ss (s);
            std::string item;

            while (getline(ss, item, delim)) {
                result.push_back (item);
            }

            return result;
    }
    public:
            void addpidtoset(int pid){
                unique_pids.insert(pid);
            }

            void writepids_time(int pid, int64_t time){
                std::ofstream outfile;
                outfile.open("/home/hravi/ghost-specialized-ps-userspace/schedulers/recorded_metrics/preemption_timeline/cfs/4_cores/metrics.info", std::ios_base::app); // append instead of overwrite
                if(!outfile.is_open()){
                    printf("hmm");
                    return;
                }
                outfile<<pid<<","<<time<<std::endl;
            }

            void writepidstofile(){
                    std::ofstream myfile("/home/hravi/ghost-specialized-ps-userspace/schedulers/cfs/pids.details");
                    if(myfile.is_open())
                    {
                        for(auto& it:unique_pids){
                            myfile<<it<< std::endl;
                        }
                        myfile.close();
                    }
            }

            // std::unordered_map<std::string,int> spec_read(){
            //         std::ifstream infile("specFile.spec");
            //         std::unordered_map<std::string,int> specs;
            //         if (infile.is_open()){
            //             std::string tp;
            //             while(getline(infile, tp)){
            //                 std::vector<std::string> tokens=split(tp,',');
            //                 specs[tokens[0]]=std::stoi(tokens[1]);
            //             }
            //             infile.close();
            //     }
            //     return specs;
            // }

            std::unordered_map<std::string,int> spec_read(std::string specfilename){
                        std::ifstream infile(specfilename);
                        int lineNo=0;
                        std::unordered_map<std::string,int> specs;
                        if (infile.is_open()){
                            std::string tp;
                            while(getline(infile, tp)){
                                if(lineNo==0){     
                                    lineNo++;
                                    continue;
                                }
                                std::vector<std::string> tokens=split(tp,',');
                                if(specs.find(tokens[0])==specs.end()){
                                    syscalls.push_back(tokens[0]);
                                }
                                specs[tokens[0]]=std::stoi(tokens[1]);
                            }
                            infile.close();
                    }
                        else{
                            printf("File not found!");
                        }
                    return specs;
            }

            bool compute_preempt_by_state(std::unordered_map<std::string,int> syscall_count){
                
                for (auto& it: syscalls) {
                    if(specs[it]<=syscall_count[it]){
                        return false;
                    }
                }
                return true;
            }

            void update_preemptionmap(){
                    general_preemption=compute_preempt_by_state(all_metrics);
                    for (auto& it: pid_metrics) {
                        allow_preemption[it.first]=compute_preempt_by_state(pid_metrics[it.first]);
                        if(!allow_preemption[it.first] && pid_metric_staleness[it.first]>absl::GetCurrentTimeNanos()){
                            // printf("Preemption to be refused for: %d\n",it.first);
                        }
                        // The allowance of preemption goes stale after 10000 ns
                    }
            }

            bool preempt_by_pid(int pid){
                if(allow_preemption.find(pid)==allow_preemption.end()){
                    return true;
                }
                if(pid_metric_staleness[pid]>absl::GetCurrentTimeNanos()){
                        if(!allow_preemption[pid]){
                            // printf("Preemption refused for %d",pid);
                        }
                         return allow_preemption[pid];
                } else{
                    return true;
                }
            }

            void all_metrics_read(std::string metrics){
                        std::ifstream infile(metrics);
                        int lineNo=0;
                        if (infile.is_open()){
                            std::string tp;
                            while(getline(infile, tp)){
                                if(lineNo==0){     
                                    lineNo++;
                                    continue;
                                }
                                std::vector<std::string> tokens=split(tp,',');
                                if(tokens[0]=="ALL"){
                                    all_metrics[tokens[1]]=std::stoi(tokens[2]);
                                } 
                                if(tokens[0]=="PID"){
                                    int pid=std::stoi(tokens[1]);
                                    if (pid_metrics.find(pid) != pid_metrics.end()){
                                        std::unordered_map<std::string,int> syscall_count_by_pid;
                                        pid_metrics[pid]=syscall_count_by_pid;
                                    }
                                    pid_metrics[pid][tokens[2]]=std::stoi(tokens[3]);
                                    pid_metric_staleness[pid]= absl::GetCurrentTimeNanos()+100000000000;
                                }
                            }
                            infile.close();
                    }
                 }
                    void init_metrics(){
                                current_path = std::filesystem::current_path();
                                printf("Current path : %s", current_path.c_str());
                                general_preemption=true;
                                specs=spec_read("/home/hravi/ghost-specialized-ps-userspace/schedulers/cfs/specFile.spec");
                                for (auto& it: specs) {
                                    printf("%s : %d", it.first.c_str(), it.second);
                                }
                        }
                    

                        void update_metrics(){

                                all_metrics_read("/home/hravi/ghost-specialized-ps-userspace/schedulers/cfs/metrics.csv");
                                // for (auto& it: specs) {
                                //     //cout << it.first.c_str()<<it.second<<endl;
                                //     printf("%s : %d", it.first.c_str(), it.second);
                                // }
                                // for(auto& it:all_metrics){
                                //     //cout<<it.first.c_str()<<" value "<<it.second<<endl;
                                //     printf("%s value: %d", it.first.c_str(), it.second);
                                // }

                                // for(auto& it:pid_metrics){
                                //     std::unordered_map<std::string,int> pid_metric_val=it.second;
                                //     for(auto& it2:pid_metric_val){
                                //                 //cout<<"PID:"<<it.first.c_str()<<" : "<<it2.first<<" :"<<it2.second<<endl;
                                //             printf("PID %d : %s : %d", it.first, it2.first.c_str(), it2.second);

                                //     }
                                // }

                        }
            };
}

#endif