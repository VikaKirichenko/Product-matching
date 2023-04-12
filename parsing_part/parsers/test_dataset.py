import pandas as pd
import csv

# df = pd.read_csv(f"urls_failed0.csv")
# # df.tail()
# print(df.shape)
# print(df.tail(30))

# with open(f"urls_failed0.csv", "r", newline="") as file:
#     reader = csv.reader(file)
#     for row in reader:
#         print(row[0])
# df_all =pd.concat([df1,df2,df3,df4])
# df_all = pd.DataFrame(columns=['sku','brand',"title", "price",'stars','url', 'description', 'specifications'])
def get_info_wb_datasets():
    all = 0
    for i in range(5):
        file_name = "dns_data_test" + str(i) + ".csv"
        df = pd.read_csv(file_name)
        # df_all = pd.concat([df_all,df])
        print(f' i = {i}, shape = {df.shape}')
        all+= df.shape[0]
    print(all)

def concat_wb_datasets(from_val,to_val):
    df_all = pd.DataFrame(columns=['sku','brand',"title", "price",'stars','url', 'description', 'specifications'])
    for i in range(5):
        file_name = "dns_data_test" + str(i) + ".csv"
        df = pd.read_csv(file_name)
        df_all = pd.concat([df_all,df])
        print(f' i = {i}, shape = {df.shape}')
    df_all['marketplace'] = ["dns"] * df_all.shape[0]
    df_all.reset_index()
    df_all.to_csv(f'dns_dataset_{from_val}_{to_val}.csv',index=False)

def concat_failed_urls():
    urls = []
    for i in range(5):
        failed_file_name = f"urls_failed{i}.csv"
        with open(failed_file_name, "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                urls.append(row[0])
    # with open("urls_failed.csv", "r", newline="") as file:
    #     reader = csv.reader(file)
    #     for row in reader:
    #         urls.append(row[0])

    with open("urls_failed_all.txt", "a", newline="") as file:
        for url in urls:
            file.write(url + "\n")

def merge_two_datasets(total_num):
    df1 = pd.read_csv("wb_dataset_1100_4000.csv")
    print(df1.shape)
    df1['marketplace'] = ["wb"] * df1.shape[0]
    df2 = pd.read_csv("wildberries_data_test.csv")
    print(df2.shape)
    df2['marketplace'] = ["wb"] * df2.shape[0]
    df_all =pd.concat([df1,df2])
    print(df_all.shape)
    df_all.reset_index()
    df_all.to_csv(f'wb_dataset_{total_num}.csv',index=False)

if __name__ == '__main__':
    #get_info_wb_datasets()

    #concat_wb_datasets(0,1281)
    # concat_failed_urls()

    df1 = pd.read_csv("wb_dataset_4000.csv")
    df2 = pd.read_csv("wb_dataset_4000_6000.csv")
    df3 = pd.read_csv("wb_dataset_6000_7000.csv")
    df4 = pd.read_csv("wb_dataset_7000_8000.csv")
    df5 = pd.read_csv("wb_dataset_8000_8270.csv")
    df_all = df_all =pd.concat([df1,df2,df3,df4,df5])
    print(df_all.shape)
    df_all.to_csv(f'wb_dataset_0_8270.csv',index=False)
    #print(df.shape)
    # df = pd.read_csv("data/wb/smartphones/smartphones_wb_all.csv")
    # print(df.shape)


#merge 2 datasets

# df1 = pd.read_csv("wb_dataset_1100_4000.csv")
# print(df1.shape)
# df1['marketplace'] = ["wb"] * df1.shape[0]
# df2 = pd.read_csv("wildberries_data_test.csv")
# print(df2.shape)
# df2['marketplace'] = ["wb"] * df2.shape[0]
# df_all =pd.concat([df1,df2])
# print(df_all.shape)
# df_all.reset_index()
# df_all.to_csv('wb_dataset_4000.csv',index=False)