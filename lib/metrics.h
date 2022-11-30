#include <metrics.h>
#include<iostream>
#include<vector>
#include<fstream>
#include <sstream>
#include<unordered_map>


namespace ghost {

    class metrics{
                 std::unordered_map<std::string,int> all_metrics;
                 std::unordered_map<int,std::unordered_map<std::string,int>> pid_metrics;
                 std::unordered_map<int,std::unordered_map<std::string,std::unordered_map<std::string,int>>> pid_task_metrics;
                 
                 std::vector<std::string> split (const std::string &s, char delim) {
                        std::vector<std::string> result;
                        std::stringstream ss (s);
                        std::string item;

                        while (getline(ss, item, delim)) {
                            result.push_back (item);
                        }

                        return result;
                    }

                    std::unordered_map<std::string,int> spec_read(){
                        std::ifstream infile("specFile.spec");
                        std::unordered_map<std::string,int> specs;
                        if (infile.is_open()){
                            std::string tp;
                            while(getline(infile, tp)){
                                std::vector<std::string> tokens=split(tp,',');
                                specs[tokens[0]]=std::stoi(tokens[1]);
                            }
                            infile.close();
                    }
                    return specs;
                    }

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
                                specs[tokens[0]]=std::stoi(tokens[1]);
                            }
                            infile.close();
                    }
                    return specs;
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
                                }
                            }
                            infile.close();
                        }
                    }
               }
    

}

