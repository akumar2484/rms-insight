<template>
	<div
      class="font-avertareguler z-40 bg-white shadow-md py-3 px-2 md:px-4 flex justify-between items-center fixed top-0 left-0 right-0 w-full duration-300"
    >
      <div class="">
        <a class="hidden lg:block md:block sm:hidden"
          ><img class="w-[200px]" src="../assets/logo.png"
        /></a>
        <a class="block lg:hidden md:hidden sm:block"
          ><img class="w-[40px] md:w-[60px]" src="../assets/fav-icon.png"
        /></a>
      </div>
      <div
        class="bg-gradient-to-t from-[#afff9f] to-[#ffffff] border md:border-2 border-gray-600 w-[147px] md:w-[210px] text-center py-1 px-2 rounded-full text-[10px] md:text-[16px] text-black duration-200"
      >
        Time
      </div>
      <div class="">
        <ul
          class="flex justify-between items-center space-x-2 md:space-x-2 text-gray-400"
        >
          <li class="pl-0 md:pl-4">
            <div class="flex items-center space-x-0 md:space-x-3">
              <div
                class="h-8 w-8 md:h-10 md:w-10 rounded-full bg-slate-50 border-2 border-gray-600 duration-200"
              >
                <!-- <img
                  class="w-full h-full rounded-full"
                  src="img/avatar-1.jpg"
                  alt=""
                /> -->
              </div>
              <p
                class="text-[#102030] text-[12px] lg:text-[14px] duration-200 hidden md:block"
              >
                Welcome,
                <strong class="font-avertaBold text-[14] lg:text-[18px]"
                  >Name</strong
                >
              </p>
            </div>
          </li>
        </ul>
      </div>
    </div>

</template>

<script setup>
</script>
