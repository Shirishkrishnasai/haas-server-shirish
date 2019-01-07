def configuration(filesize, vcores):
    blocksize = 128

    map_tasks = int(filesize) / int(blocksize)

    configurations_dict = {}
    if map_tasks <= vcores:
        configurations_dict["total_map_tasks"] = map_tasks
    else:
        configurations_dict["total_map_tasks"] = vcores

    configurations_dict["reducer_tasks"] = configurations_dict["total_map_tasks"] * 0.5

    if configurations_dict["total_map_tasks"] < 2:
        configurations_dict["total_map_tasks"] = 2
    if configurations_dict["reducer_tasks"] < 2:
        configurations_dict["reducer_tasks"] = 2
    javaopts = 400
    configurations_dict["sortmb"] = int(0.4 * javaopts)
    configurations_dict["sortfactor"] = int(configurations_dict["sortmb"] / 10)
    configurations_dict["map_output_compress"] = 'true'
    configurations_dict["javaopts"] = "-Xmx" + str(javaopts) + "m"

    return configurations_dict
