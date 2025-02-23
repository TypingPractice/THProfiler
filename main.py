import argparse
from pathlib import Path, PurePosixPath
from typing import Optional, List

from DegreeCentrality.file_util import *
from DegreeCentrality.degree import *
from DegreeCentrality.drh_deal import *
from DegreeCentrality.recommender import recommend_by_degree, recommend_by_maintenance, recommend_by_drh
from DegreeCentrality.xml_to_json import xml_to_json
from MaintenanceCostMeasurement.gitlogprocessor import *
from MaintenanceCostMeasurement.getnode import *
from MaintenanceCostMeasurement.changeproness import *
from TypingCoverageDetection.main import CovEntry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', '-d', action='store', dest='project_root',
                        help='root directory of project')
    parser.add_argument('--stub', '-s', action='store', dest='stub_root',
                        help='stub file directory if stub files are created as different project, '
                             'default value is project root directory')
    parser.add_argument('--name', '-n', action='store', dest='project_name',
                        help='specify project name')
    parser.add_argument('--out', action='store', dest='out_url')
    parser.add_argument('--coverage', '-c', action='store_true', dest='coverage', default=False)

    parser.add_argument('--degree', action='store_true', dest='degree', default=False)
    parser.add_argument('--dep', action='store', dest="dependency",
                        help='specify dependency file location')
    parser.add_argument('--filetype', '-ft', action='store', dest='filetype', help='specify out file type location')
    parser.add_argument('--degree_out', '-do', action='store', dest='degree_output',
                        help='specify degree output file name')
    parser.add_argument('--statistic', action='store', dest='statistic',
                        help='specify the output of statistic of the proportion of each distribution')

    parser.add_argument('--merge', action='store', metavar=('ARG1', 'ARG2', 'ARG3'), nargs=3, dest='merge',
                        default=False,
                        help='merge ARG1 and ARG2 into ARG3')
    parser.add_argument('--from-understand', nargs=3, action='store', dest='from_understand')

    parser.add_argument('-drh', nargs=1, metavar=('drh_URL'), action='store', dest='drh_method')

    parser.add_argument('--measure', action='store_true', dest='measure', default=False,
                        help="analyzes the maintenance cost of typed and untyped files according to the revision "
                             "history managed by VCS")
    parser.add_argument('--sort-by', action='store', dest='sort_by',
                        help="if sort ")
    parser.add_argument('--intersection', action='store_true', dest='intersection', default=True,
                        help="output the intersection set of selected features")
    parser.add_argument('--union', action='store_false', dest='intersection',
                        help="output the union set of selected features")
    parser.add_argument('--feature',metavar=("f1,f2...",), action='store', dest='feature',
                        help="list of features for recommending, separated by comma(,). "
                             "Supported features contain degree, drh and maintenance.")
    parser.add_argument('--top', metavar=("k1,k2...",) ,action='store', dest='top',
                        help="recommend top k1﹪ files of feature f1")

    args = parser.parse_args()
    dispatch(args)


def dispatch_feature(src_dir: Path, features: List[str], top: Optional[str], args):
    rank_rates: List[float]
    default_rate = 0.1
    if top is not None:
        rank_rates = [float(x) * 0.01 for x in top.split(",")]
    else:
        rank_rates = []

    intersection_recommend_set = set()
    union_recommend_set = set()
    recommend_res = []
    for feature in features:
        recommend_lst = []
        if feature == "degree":
            rate = default_rate if len(rank_rates) == 0 else rank_rates.pop(0)
            recommend_lst = recommend_by_degree(rate, args.dependency)
            # print("Recommend file by degree(top %{} files are recommended):".format(rate * 100))
            # for file in recommend_lst:
            #     print(file)
        elif feature == "drh":
            recommend_lst = recommend_by_drh(args.drh_method[0])
        elif feature == "maintenance":
            rate = default_rate if len(rank_rates) == 0 else rank_rates.pop(0)
            if args.sort_by is not None:
                recommend_lst = recommend_by_maintenance(src_dir, rate, args.sort_by)
            else:
                recommend_lst = recommend_by_maintenance(src_dir, rate)
        recommend_res.append(set(recommend_lst))
        union_recommend_set.update(recommend_lst)
    if len(recommend_res) > 0:
        intersection_recommend_set = recommend_res[0]
    else:
        return
    for i in range(1, len(recommend_res)):
        intersection_recommend_set = intersection_recommend_set.intersection(recommend_res[i])

    if args.intersection:
        recommend_result = intersection_recommend_set
        print("intersection of recommended file: ")
    else:
        recommend_result = union_recommend_set
        print("union of recommended file: ")
    for file in recommend_result:
        print(str(file).replace("\\", os.sep).replace("/", os.sep))



def dispatch(args):
    if not hasattr(args, 'project_root'):
        raise ValueError("root directory of project must supply, see -h for more detailed")

    src_dir = Path(args.project_root)
    if args.stub_root is not None:
        stub_dir = Path(args.stub_root)
    else:
        stub_dir = src_dir
    if args.project_name is not None:
        project_name = args.project_name
    else:
        project_name = src_dir.name

    if args.coverage:
        CovEntry(src_dir, stub_dir, project_name)

    if args.degree:
        try:
            degree_out = args.degree_output
            statistic_out = args.statistic
            get_degree(args.dependency, args.filetype, degree_out, statistic_out)
        except AttributeError:
            print("Option error in degree, if you specified degree option,"
                  " degree-output, statistic, dependency and filetype option shouled also be specified")



    if args.merge:
        merge(*args.merge)

    if args.from_understand:
        xml_to_json(*args.from_understand)

    if args.measure:
        rootDir = str(src_dir.absolute().parent).replace("\\", "/") + "/"
        gitlog(rootDir, project_name)
        dir = rootDir + project_name
        mc_file = rootDir + project_name + '/mc/history-py.csv'
        outfile = rootDir + project_name + '/mc/file-mc.csv'
        node_url = rootDir + project_name + "-node.csv"
        get_nodefile(dir, node_url)
        changeproness(node_url, mc_file, outfile)

    if args.feature:
        features = args.feature

        dispatch_feature(src_dir, features.split(","), args.top, args)


def RQ23Entry():
    # input
    explicit_url = 'C:/Users/ZDH/Documents/WeChat Files/wxid_4fylpmco0bfg22/FileStorage/File/2021-05/result-0325/result-0325/matplotlib/matplotlib.json'  # Understand result
    possible_url = 'C:/Users/ZDH/Documents/WeChat Files/wxid_4fylpmco0bfg22/FileStorage/File/2021-05/result-0325/result-0325/matplotlib/matplotlib-deps-from-type.json'  # ENRE result
    typed_url = 'C:/Users/ZDH/Documents/WeChat Files/wxid_4fylpmco0bfg22/FileStorage/File/2021-05/result-0325/result-0325/matplotlib/matplotlibFileType.csv'  # File type
    drh_url = 'C:/Users/ZDH/Documents/WeChat Files/wxid_4fylpmco0bfg22/FileStorage/File/2021-05/result-0325/result-0325/matplotlib/out/matplotlib-drh.json'  # Drh result
    rootDir = 'E:/Master/Python/Coverage_Data_Set/matplotlib'  # The repository path cloned from GitHub
    projectName = 'matplotlib'  # The name of project, eg:spark
    output_url = 'C:/Users/ZDH/Documents/WeChat Files/wxid_4fylpmco0bfg22/FileStorage/File/2021-05/result-0325/result-0325/matplotlib/out'  # The target path to output

    # output
    dependency_url = output_url + projectName + '.json'
    degree_url = output_url + projectName + '_degree.csv'
    statistic_url = output_url + projectName + '_statistics.csv'
    drh_out = output_url + projectName + '_drh.csv'
    drh_statistic = output_url + projectName + '_drhstatistics.csv'
    node_url = rootDir + projectName + "-node.csv"
    mc_file = rootDir + projectName + '/mc/history-py.csv'  # 'C:/Users/ding7/Desktop/gitrepo/numpy/mc/history-all.csv'
    outfile = rootDir + projectName + '/mc/file-mc.csv'  # "C:/Users/ding7/Desktop/gitrepo/numpy/mc/file-mc.csv"

    # rq2
    merge(explicit_url, possible_url, dependency_url)
    G, variables = create_graph(dependency_url)
    degree_processing(G, variables, typed_url, degree_url, statistic_url)

    drh_statistical(drh_url, drh_out)

    # rq3
    gitlog(rootDir, projectName)
    dir = rootDir + projectName  # "C:/Users/ding7/Desktop/gitrepo/numpy"
    get_nodefile(dir, node_url)
    changeproness(node_url, mc_file, outfile)


if __name__ == '__main__':
    main()
