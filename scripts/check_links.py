import os
import urllib.request
from bs4 import BeautifulSoup
import markdown
from texttable import Texttable


# Currently not in use because Sphinx generated html files
# do not show in the Peekingduck repo on github
#
# def get_html():
#     lst_html = []
#     # search path is hard coded with ref of this script locaiton
#     for root, dirs, files in os.walk(
#         os.path.join(".", "docs", "build", "html"), topdown=False
#     ):
#         for name in files:
#             if name[-4:] == "html":
#                 filepath = os.path.join(root, name)
#                 lst_html.append((filepath, root))
#     return lst_html


def get_md_rst():
    lst_md_rst = []
    # search path is hard coded with ref to github actions
    # will ref to Peekingduck root folder
    for root, dirs, files in os.walk(".", topdown=False):
        for name in files:
            if name[-2:] == "md" or name[-3:] == "rst":
                filepath = os.path.join(root, name)
                lst_md_rst.append((filepath, root))
    return lst_md_rst


def check_files(lst_filepaths):
    faulty_links = []
    for filepath, root in lst_filepaths:

        with open(filepath, "r", encoding="utf-8") as f:
            file = f.read()
            file_as_html = markdown.markdown(file)
            soup = BeautifulSoup(file_as_html, "html.parser")
            filtered_by_img_tags = soup.find_all("img")
            filtered_by_href_tags = soup.find_all("a")
            img_links = [
                tag["src"] for tag in filtered_by_img_tags if tag.has_attr("src")
            ]
            href_links = [
                tag["href"] for tag in filtered_by_href_tags if tag.has_attr("href")
            ]
            total_list_of_links = img_links + href_links
            final_list_of_links = [txt for txt in total_list_of_links if ("." in txt)]
            # to extract the valid link from some links such as ./io_draw_nodes.md#input-nodes
            final_list_of_links = [link.split("#")[0] for link in final_list_of_links]

        for link in final_list_of_links:
            # if link is a https link, run request.urlopen
            if link[:4] == "http":
                try:
                    resp = urllib.request.urlopen(link)  # nosec
                except Exception as e:
                    # In this implementation only 404 is flagged for broken links
                    # 404 = http page not found error
                    # if statement can be removed/adjusted to flag multiple error codes
                    # such as 404,403,408...
                    if e.code == 404:
                        # filepath is the current file being parsed
                        # link is the link found in the current parsed file
                        # e.code is the execption code
                        faulty_links.append([filepath, link, e.code])

            else:
                check = os.path.exists(os.path.join(root, link))

                if not check:
                    # filepath is the current file being parsed
                    # link is the link found in the current parsed file
                    # root is the root folder of the filepath of current file
                    condition = ["/peekingduck", "pipeline", "nodes"]
                    if link.split(".")[0:3] == condition:
                        pass

                    else:
                        faulty_links.append([filepath, link, root])

        print(f"Checked {filepath}")

    return faulty_links


def print_output(faulty_links):

    print("\nTable of broken links\n")
    t = Texttable()
    t.set_cols_width([25, 25, 20])
    t.add_rows(
        [["Filepath", "Broken_Link", "Root_Folder / Request Error Code"]] + faulty_links
    )
    print(t.draw())


if __name__ == "__main__":

    mds_rst_filepaths = get_md_rst()
    print("\nCHECKING FILES")
    print("-" * 50)
    faulty_links = check_files(mds_rst_filepaths)

    print_output(faulty_links)

