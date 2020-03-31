from git import Repo
from git import RemoteProgress
from pathlib import Path

class RepoManager:
    @staticmethod
    def update_repo(repository_path, base_output_path='.'):
        head_file = Path(f'{base_output_path}/lastrev')
        if head_file.is_file():
            with open(head_file, 'r') as file:
                c_ref = file.read().replace('\n', '')
                file.close()
        else:
            c_ref = None

        repo = Repo(repository_path)
        o = repo.remotes.origin
        for fetch_info in o.pull(progress=MyProgressPrinter()):
            print("Updated %s to %s" % (fetch_info.ref, fetch_info.commit))
            last_rev = f'{fetch_info.commit}'
            if c_ref == last_rev:
                return False
            else:
                print(f'{fetch_info.commit}')
                with open(head_file, 'w+') as file:
                    file.write(last_rev)
                    file.close()
                return True


class MyProgressPrinter(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        print(op_code, cur_count, max_count, cur_count / (max_count or 100.0), message or "NO MESSAGE")