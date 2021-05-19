### DegreeCentrality
This module computes the degree centrality for files based on the ADG built by Dependency Structure Analysis.    
To calculate the degree centrality, you should give it the dependency file, which is in JSON format, of the project you need to analysis.  
```sh
python main.py --degree <dependency file>
```
If you want compute degree centrality by multiple dependency files, you should merge these dependency files first.
```sh
python main.py --merge <dependency file1> <dependency file2> <output dependency file>
```
### MaintenanceCostMeasurement
Based on commit records, this module quantifies the effort taken on maintaining source files.   
Six measures are computed, including #commit—the number of commits made to a file; #changeLoc—the total lines of changed code of modifying a file; #author—the number of developers for maintaining a file; issue—the number of issues that a file gets involved; #issueCmt—the numberf commits of a file for fixing issues; #issueLoc—the total LoC changed to a file for fixing issues.
To use this module you should provide a git repository to THProfiler.
```sh
python main.py --directory <git repository> --measure
```