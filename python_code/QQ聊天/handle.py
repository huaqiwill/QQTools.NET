from datetime import datetime, timedelta

import pandas

# 日期规范化

def convert_time(time_str):
    # 获取当前日期和时间
    now = datetime.now()

    # 处理 "星期几" 格式
    if "星期" in time_str:
        # 提取星期几和时间部分
        weekday_str, time_part = time_str.split()

        # 中文星期几映射到数字（0=周一，6=周日）
        weekday_map = {
            "星期一": 0,
            "星期二": 1,
            "星期三": 2,
            "星期四": 3,
            "星期五": 4,
            "星期六": 5,
            "星期日": 6
        }

        # 计算目标日期
        target_weekday = weekday_map[weekday_str]
        current_weekday = now.weekday()  # 当前星期几（0=周一，6=周日）

        # 计算距离目标星期几的天数
        delta_days = (target_weekday - current_weekday) % 7
        target_date = now + timedelta(days=delta_days)

        # 如果目标日期比当前日期晚，减去一周
        if target_date > now:
            target_date -= timedelta(days=7)

        # 组合日期和时间
        return target_date.strftime("%Y/%m/%d ") + time_part

    # 处理 "昨天 14:37" 格式
    elif "昨天" in time_str:
        # 减去一天
        target_date = now - timedelta(days=1)
        time_part = time_str.split()[-1]
        return target_date.strftime("%Y/%m/%d ") + time_part

    # 处理其他格式（如今天）
    elif "今天" in time_str:
        time_part = time_str.split()[-1]
        return now.strftime("%Y/%m/%d ") + time_part
    elif "前天" in time_str:
        # 减去两天
        target_date = now - timedelta(days=2)
        time_part = time_str.split()[-1]
        return target_date.strftime("%Y/%m/%d ") + time_part
    else:
        return time_str

def msg_csv_eq(message_path):
    df = pandas.read_csv(message_path, header=None,
                         names=("time", "name", "text"),
                         dtype={"time": str, "name": str, "text": str})
    print(df.shape)

    df = df[~df["text"].isna() & ~df["text"].str.strip().eq("")]

    df["time"] = df["time"].ffill()  # 用上方非空值填充
    df["time"] = df["time"].bfill()  # 用下方非空值填充
    # 日期规范化
    df["time"] = df["time"].apply(convert_time)
    # 输出结果
    df.to_csv(message_path, index=False)
    # 保存成功
    print("数据保存成功")

if __name__ == '__main__':
    msg_csv_eq("智能汽车竞赛创意组.csv")